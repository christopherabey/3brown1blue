from scene_generator import SceneGenerator

test_transcriptions = [
    "The quick brown fox jumps over the lazy dog.",
]

sg = SceneGenerator(test_transcriptions)
sg.generate_all_scenes()