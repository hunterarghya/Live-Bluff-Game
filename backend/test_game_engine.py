from game_logic import BluffGame

# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def banner(title):
    print("\n" + "=" * 70)
    print(f"TEST: {title}")
    print("=" * 70 + "\n")

def assert_eq(a, b, msg=""):
    if a != b:
        raise AssertionError(f"ASSERT FAILED: {a} != {b} | {msg}")

def assert_true(cond, msg=""):
    if not cond:
        raise AssertionError(f"ASSERT FAILED: {msg}")

# -------------------------------------------------
# TESTS
# -------------------------------------------------

def test_deal_cards():
    banner("DEAL CARDS")

    g3 = BluffGame(["A", "B", "C"])
    counts3 = [len(g3.player_hands[p]) for p in g3.players]
    assert_eq(sum(counts3), 51, "3-player total cards incorrect")

    g4 = BluffGame(["A", "B", "C", "D"])
    counts4 = [len(g4.player_hands[p]) for p in g4.players]
    assert_eq(sum(counts4), 52, "4-player total cards incorrect")

    print("PASS: Deal logic OK")


def test_turn_enforcement():
    banner("TURN ENFORCEMENT")

    g = BluffGame(["A", "B", "C"])

    try:
        g.play_cards("B", ["2♠"], "2")
        raise AssertionError("Allowed out-of-turn play")
    except ValueError:
        pass

    print("PASS: Turn enforcement OK")


def test_claim_lock():
    banner("CLAIM LOCK")

    g = BluffGame(["A", "B", "C"])
    g.player_hands = {
        "A": ["Q♠", "Q♥"],
        "B": ["2♠"],
        "C": ["3♠"],
    }

    g.play_cards("A", ["Q♠"], claim_rank="Q")

    try:
        g.play_cards("B", ["2♠"], claim_rank="K")
        raise AssertionError("Allowed claim change mid-pile")
    except ValueError:
        pass

    print("PASS: Claim lock enforced")


def test_all_pass_dump():
    banner("ALL PASS DUMP")

    g = BluffGame(["A", "B", "C"])
    g.player_hands = {
        "A": ["2♠", "3♠"],
        "B": ["4♠"],
        "C": ["5♠"],
    }

    g.play_cards("A", ["2♠"], claim_rank="2")
    g.pass_turn("B")
    g.pass_turn("C")
    g.pass_turn("A")

    assert_eq(len(g.pile), 0, "Pile not dumped")
    assert_true(g.claim_rank is None, "Claim not reset")

    print("PASS: All-pass dump works")


def test_doubt_on_lie():
    banner("DOUBT ON LIE")

    g = BluffGame(["A", "B", "C"])
    g.player_hands = {
        "A": ["Q♠", "9♠"],   # ensure NOT last card
        "B": ["2♠"],
        "C": ["3♠"],
    }

    g.play_cards("A", ["Q♠"], claim_rank="K")  # lie
    g.pass_turn("B")
    result = g.call_doubt("C")

    assert_eq(result["result"], "lie")
    assert_eq(result["loser"], "A")
    assert_eq(len(g.player_hands["A"]), 2, "Pile not given to liar")

    print("PASS: Doubt on lie works")


def test_doubt_on_truth():
    banner("DOUBT ON TRUTH")

    g = BluffGame(["A", "B", "C"])
    g.player_hands = {
        "A": ["Q♠", "Q♥"],  # NOT last card
        "B": ["2♠"],
        "C": ["3♠"],
    }

    g.play_cards("A", ["Q♠"], claim_rank="Q")
    g.pass_turn("B")
    result = g.call_doubt("C")

    assert_eq(result["result"], "truth")
    assert_eq(result["loser"], "C")
    assert_eq(len(g.player_hands["C"]), 2, "Pile not given to doubter")

    print("PASS: Doubt on truth works")


def test_game_over():
    banner("GAME OVER")

    g = BluffGame(["A", "B"])
    g.player_hands = {
        "A": ["A♠"],
        "B": ["2♠"],
    }

    res = g.play_cards("A", ["A♠"], claim_rank="A")
    assert_eq(res["event"], "game_over")
    assert_eq(res["winner"], "A")

    try:
        g.pass_turn("B")
        raise AssertionError("Allowed move after game over")
    except ValueError:
        pass

    print("PASS: Game over enforced")


# -------------------------------------------------
# RUNNER
# -------------------------------------------------

if __name__ == "__main__":
    test_deal_cards()
    test_turn_enforcement()
    test_claim_lock()
    test_all_pass_dump()
    test_doubt_on_lie()
    test_doubt_on_truth()
    test_game_over()

    print("\n✅ ALL TESTS PASSED SUCCESSFULLY\n")
