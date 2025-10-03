import sys
sys.path.insert(0, './src')

from pipeline import main

def test_main_runs():
    ranked, news_results, decisions = main()
    assert ranked is not None
    assert isinstance(news_results, list)
    assert isinstance(decisions, dict)

if __name__ == "__main__":
    test_main_runs()
    print("Pipeline test passed!")
