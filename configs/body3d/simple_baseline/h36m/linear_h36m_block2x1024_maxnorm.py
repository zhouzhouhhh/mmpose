log_level = 'INFO'
load_from = None
resume_from = None
dist_params = dict(backend='nccl')
workflow = [('train', 1)]
checkpoint_config = dict(interval=10)
evaluation = dict(
    interval=10, metric=['mpjpe', 'p-mpjpe'], key_indicator='mpjpe')

# optimizer settings
optimizer = dict(
    type='Adam',
    lr=1e-4,  # The original paper uses 1e-3.
)
optimizer_config = dict(grad_clip=None)
# learning policy
lr_config = dict(
    policy='step',
    by_epoch=False,
    step=100000,
    gamma=0.96,
)

total_epochs = 200

log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        # dict(type='TensorboardLoggerHook')
    ])

channel_cfg = dict(
    num_output_channels=17,
    dataset_joints=17,
    dataset_channel=[
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    ],
    inference_channel=[
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16
    ])

# model settings
model = dict(
    type='PoseLifter',
    pretrained=None,
    backbone=dict(
        type='TCN',
        in_channels=2 * 16,
        stem_channels=1024,
        num_blocks=2,
        kernel_sizes=(1, 1, 1),
        dropout=0.5,
        max_norm=1.0),
    keypoint_head=dict(
        type='TemporalRegressionHead',
        in_channels=1024,
        num_joints=16,
        max_norm=1.0,
        loss_keypoint=dict(type='MSELoss')),
    train_cfg=dict(),
    test_cfg=dict())

# data settings
data_root = 'data/h36m'
data_cfg = dict(
    num_joints=17,
    seq_len=1,
    seq_frame_interval=1,
    casual=True,
    joint_2d_src='gt',
    need_camera_param=False,
    camera_param_file=f'{data_root}/annotation_body3d/cameras.pkl',
)

train_pipeline = [
    dict(
        type='JointRelativization',
        item='target',
        visible_item='target_visible',
        root_index=0,
        root_name='global_position',
        remove_root=True),
    dict(
        type='JointNormalization',
        item='target',
        norm_param_file=f'{data_root}/annotation_body3d/joint3d_rel_stats.pkl'
    ),
    dict(
        type='JointRelativization',
        item='input_2d',
        visible_item='input_2d_visible',
        root_index=0,
        remove_root=True),
    dict(
        type='JointNormalization',
        item='input_2d',
        norm_param_file=f'{data_root}/annotation_body3d/joint2d_rel_stats.pkl'
    ),
    dict(type='PoseSequenceToTensor', item='input_2d'),
    dict(
        type='Collect',
        keys=[('input_2d', 'input'), 'target'],
        meta_name='metas',
        meta_keys=[
            'target_image_path', 'flip_pairs', 'global_position',
            'global_position_index', 'target_mean', 'target_std'
        ])
]

val_pipeline = train_pipeline
test_pipeline = val_pipeline

data = dict(
    samples_per_gpu=64,
    workers_per_gpu=2,
    val_dataloader=dict(samples_per_gpu=64),
    test_dataloader=dict(samples_per_gpu=64),
    train=dict(
        type='Body3DH36MDataset',
        ann_file=f'{data_root}/annotation_body3d/h36m_train.npz',
        img_prefix=f'{data_root}/images/',
        data_cfg=data_cfg,
        pipeline=train_pipeline),
    val=dict(
        type='Body3DH36MDataset',
        ann_file=f'{data_root}/annotation_body3d/h36m_test.npz',
        img_prefix=f'{data_root}/images/',
        data_cfg=data_cfg,
        pipeline=val_pipeline),
    test=dict(
        type='Body3DH36MDataset',
        ann_file=f'{data_root}/annotation_body3d/h36m_test.npz',
        img_prefix=f'{data_root}/images/',
        data_cfg=data_cfg,
        pipeline=test_pipeline),
)
