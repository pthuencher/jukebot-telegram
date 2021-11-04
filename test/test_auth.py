from src.auth import load_whitelist, save_whitelist

TEST_WHITELIST_FILE = "test/test_whitelist.txt"

def test_load_whitelist():
    with open(TEST_WHITELIST_FILE, "w") as fd:
        fd.write("327452635\n437253453\n123123456\n")

    whitelist = load_whitelist(TEST_WHITELIST_FILE)
    assert len(whitelist) == 3
    assert whitelist[0] == 327452635
    assert whitelist[1] == 437253453
    assert whitelist[2] == 123123456

def test_save_whitelist():

    new_whitelist = [1, 2, 3]
    assert save_whitelist(TEST_WHITELIST_FILE, new_whitelist) == True

    whitelist = load_whitelist(TEST_WHITELIST_FILE)
    assert len(whitelist) == 3
    assert whitelist[0] == 1
    assert whitelist[1] == 2
    assert whitelist[2] == 3

    new_whitelist = [327452635, 437253453, 123123456]
    assert save_whitelist(TEST_WHITELIST_FILE, new_whitelist) == True

    whitelist = load_whitelist(TEST_WHITELIST_FILE)
    assert len(whitelist) == 3
