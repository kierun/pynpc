# -*- coding: utf-8 -*-
"""Name corruptor tests."""
from pathlib import Path

import pytest
from orjson import loads

from pynpc.name_corruptor import NameCorruptor, parse_patterns


def test_parse_single_sequence():
    assert parse_patterns([["a", "b", "c"]]) == [("a", "b"), ("b", "c")]


def test_parse_multiple_sequences():
    sut = [
        ["a", "b", "c"],
        ["d", "e", "f"],
    ]
    expected = [
        ("a", "b"),
        ("b", "c"),
        ("d", "e"),
        ("e", "f"),
    ]
    assert parse_patterns(sut) == expected


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("agatha", "agadda agata"),
        ("aldwin", "altwen altwin altwum altwun"),
        ("althea", "alddea altea"),
        ("anselm", "aintzelm aiwantzelm antzelm intzelm"),
        ("armin", "armen armium armum armun"),
        ("bartholomew", "barddolomew bartolomew fartolomew partolomew"),
        ("berengar", "baerengar baeriumgar baerumgar baerungar"),
        ("clarice", "claricke clarihjke clarijke clarike"),
        ("constance", "khonstaince khonstance khonstince konstance"),
        ("dierk", "dieyrk tieyrk tiheyrk tyeyrk"),
        ("eadric", "eadrick eadrijk eadrik eatrijk"),
        ("edward", "echard echart edvard etvard"),
        ("eldrida", "eltrihta eltrita eltryta"),
        ("elfric", "elfrick elfrijk elfrik elvrijk"),
        ("erna", "aerne erne"),
        ("eustace", "eustache eusteeche eusteeckhe eusteiche"),
        ("felicity", "velicity vhelicity vhelihcihty vhelycyty"),
        ("finnegan", "vhennegan vhinnegan vhunnegan vinnegan"),
        ("giselle", "gihtzellya gitzella gitzelle gitzellya"),
        ("gerald", "gaerald gaeralt gaidralt gairalt"),
        ("godric", "godrick godrijk godrik gotrijk"),
        ("gunther", "gumtaer gundder guntaer gunter"),
        ("hadrian", "hatrian hatrihan hatryan hatryin"),
        ("heloise", "heloihse heloite heloize heloyse"),
        ("isolde", "ihsolte isolte izolte ysolte"),
        ("ivor", "ihvhor ivhor yvhhor yvhor"),
        ("jocelyn", "jocielyn joselyn jotzelyn"),
        ("lancelot", "lancielot lanselot lantzelod lantzelot"),
        ("lysandra", "lytsandra lytzahndra lytzahntra lyzandra"),
        ("magnus", "magnaes magnees"),
        ("melisande", "melitsande melitzahnde melitzahnte melizande"),
        ("merrick", "maerrijkk merrickk merrijkk merrikk"),
        ("osborn", "osforn osporn osvhorn osvorn"),
        ("philomena", "ffilomena filomena vhilomena vilomena"),
        ("reginald", "regenelt regineld reginelt regunelt"),
        ("rowena", "rowene rowiume rowume rowune"),
        ("sabine", "tsabine tzahbene tzahbine zabine"),
        ("seraphina", "seraffina serafina seravhina seravina"),
        ("sigfrid", "sigvhrid sigvhrit sigvrid sihgvhriht"),
        ("tiberius", "tibaerius tihbaerihus tybaeryus typaeryus"),
        ("ulf", "ulv ulvh"),
        ("urien", "urieyn uriheyn uryeyn"),
        ("vespera", "vhesfaera vhesfaira vhespaera vhespera"),
        ("wendel", "wentel wiumtel wumtel wuntel"),
        ("wilfred", "wihlvhret wilvhred wilvhret wilvred"),
        ("winifred", "wenivhret winivhred winivhret winivred"),
        ("xenia", "xihumiha xiumia xumia xunia"),
        ("ysabel", "ytsabel ytzahbel ytzahpel yzabel"),
        ("zephyr", "zeffyr zefyr zevhyr zevyr"),
        ("zinnia", "zennia ziumnia zumnia zunnia"),
        ("zuriel", "tzuryeyl zurieyl zuriheyl zuryeyl"),
        ("zygmund", "zygmihumt zygmiumt zygmumt zygmunt"),
    ],
)
def test_corrupt_several(name, expected):
    data = Path(Path(__file__).resolve().parent.parent, "pynpc", "data", "name-corruption-pattern.json")
    patterns = parse_patterns(loads(data.read_text()))

    corruptor = NameCorruptor(patterns)
    generated = corruptor.corrupt(name, 4)
    assert " ".join(generated) == expected, " ".join(generated)


def test_latesha_hanging() -> None:
    """Test that Latesha is hanging."""
    data = Path(Path(__file__).resolve().parent.parent, "pynpc", "data", "name-corruption-pattern.json")
    patterns = parse_patterns(loads(data.read_text()))
    sut = NameCorruptor(patterns)
    assert "Lataersha" in sut.corrupt("Latersha")
