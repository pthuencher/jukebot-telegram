from src.utils import youtube_dl_info, youtube_dl_download, sanitize_url, validate_ext, validate_length


def test_sanitize_url_playlist_param():
    samples: list = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL634F2B56B8C346A2", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    ]

    for sample in samples:
        assert sanitize_url(sample[0]) == sample[1]

def test_validate_ext():
    samples: list = [
        ("video", "video"),
        ("audio", "audio"),
        ("audiovideo", False),
        ("§§§€€€€", False),
        ("\x13\x12\x11", False)
    ]

    for sample in samples:
        assert validate_ext(sample[0]) == sample[1]

def test_validate_length():
    samples: list = [
        ("full", "full"),
        ("00:01:30-00:02:50", "00:01:30-00:02:50"),
        ("00:0:30-0:02:50", "00:0:30-0:02:50"),
        ("00:00:01:30-00:02:50", False),
        ("00:01:30-00:02", False),
        ("-00:02:50", False),
        ("00:01:30|00:02:50", False)
    ]

    for sample in samples:
        assert validate_length(sample[0]) == sample[1]

# def test_youtube_dl_info():
#     samples: list = [
#         ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
#         ("https://www.youtube.com/watch?v=oQ9GCO1cnMY", "oQ9GCO1cnMY"),
#     ]
    
#     for sample in samples:
#         info: dict = youtube_dl_info(sample[0])
#         assert info["id"] == sample[1]

# def test_youtube_dl_download():

#     assert 1 == 1