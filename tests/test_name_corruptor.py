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


def test_corrupt_once():
    corruptor = NameCorruptor(parse_patterns([["th", "ff"]]))
    assert corruptor.corrupt_once("agatha") == "agaffa"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("agatha", "agatha agadda agata agata agata"),
        ("aldwin", "aldwin altwin altwen altwun altwum"),
        ("althea", "althea alddea altea altea altea"),
        ("anselm", "anselm antzelm intzelm aintzelm aiwantzelm"),
        ("armin", "armin armen armun armum armium"),
        (
            "bartholomew",
            "bartholomew barddolomew bartolomew partolomew fartolomew",
        ),
        ("berengar", "berengar baerengar baerungar baerumgar baeriumgar"),
        ("clarice", "clarice claricke clarike clarijke clarihjke"),
        (
            "constance",
            "constance konstance khonstance khonstince khonstaince",
        ),
        ("dierk", "dierk dieyrk tieyrk tiheyrk tyeyrk"),
        ("eadric", "eadric eadrick eadrik eadrijk eatrijk"),
        ("edward", "edward edvard etvard echard echart"),
        ("eldrida", "eldrida eltrita eltrihta eltryta eltryta"),
        ("elfric", "elfric elfrick elfrik elfrijk elvrijk"),
        ("erna", "erna erne aerne aerne aerne"),
        ("eustace", "eustace eustache eusteiche eusteeche eusteeckhe"),
        ("felicity", "felicity velicity vhelicity vhelihcihty vhelycyty"),
        ("finnegan", "finnegan vinnegan vhinnegan vhennegan vhunnegan"),
        ("giselle", "giselle gitzelle gitzella gitzellya gihtzellya"),
        ("gerald", "gerald gaerald gaeralt gairalt gaidralt"),
        ("godric", "godric godrick godrik godrijk gotrijk"),
        ("gunther", "gunther gundder gunter guntaer gumtaer"),
        ("hadrian", "hadrian hatrian hatrihan hatryan hatryin"),
        ("heloise", "heloise heloihse heloyse heloize heloite"),
        ("isolde", "isolde isolte ihsolte ysolte izolte"),
        ("ivor", "ivor ivhor ihvhor yvhor yvhhor"),
        ("jocelyn", "jocelyn jocielyn joselyn jotzelyn jotzelyn"),
        ("lancelot", "lancelot lancielot lanselot lantzelot lantzelod"),
        ("lysandra", "lysandra lyzandra lytsandra lytzahndra lytzahntra"),
        ("magnus", "magnus magnaes magnees magnees magnees"),
        (
            "melisande",
            "melisande melizande melitsande melitzahnde melitzahnte",
        ),
        ("merrick", "merrick merrickk merrikk merrijkk maerrijkk"),
        ("osborn", "osborn osporn osforn osvorn osvhorn"),
        ("philomena", "philomena ffilomena filomena vilomena vhilomena"),
        ("reginald", "reginald regineld reginelt regenelt regunelt"),
        ("rowena", "rowena rowene rowune rowume rowiume"),
        ("sabine", "sabine zabine tsabine tzahbine tzahbene"),
        ("seraphina", "seraphina seraffina serafina seravina seravhina"),
        ("sigfrid", "sigfrid sigvrid sigvhrid sigvhrit sihgvhriht"),
        ("tiberius", "tiberius tibaerius tihbaerihus tybaeryus typaeryus"),
        ("ulf", "ulf ulv ulvh ulvh ulvh"),
        ("urien", "urien urieyn uriheyn uryeyn uryeyn"),
        ("vespera", "vespera vhespera vhespaera vhesfaera vhesfaira"),
        ("wendel", "wendel wentel wuntel wumtel wiumtel"),
        ("wilfred", "wilfred wilvred wilvhred wilvhret wihlvhret"),
        ("winifred", "winifred winivred winivhred winivhret wenivhret"),
        ("xenia", "xenia xunia xumia xiumia xihumiha"),
        ("ysabel", "ysabel yzabel ytsabel ytzahbel ytzahpel"),
        ("zephyr", "zephyr zeffyr zefyr zevyr zevhyr"),
        ("zinnia", "zinnia zennia zunnia zumnia ziumnia"),
        ("zuriel", "zuriel zurieyl zuriheyl zuryeyl tzuryeyl"),
        ("zygmund", "zygmund zygmunt zygmumt zygmiumt zygmihumt"),
    ],
)
def test_corrupt_several(name, expected):
    data = Path(Path(__file__).resolve().parent.parent, "pynpc", "data", "name-corruption-pattern.json")
    patterns = parse_patterns(loads(data.read_text()))

    corruptor = NameCorruptor(patterns)
    generated = [name]
    for _ in range(len(expected.split(" ")) - 1):
        _next = generated[-1]
        corrupted = corruptor.corrupt_once(_next)
        generated.append(corrupted)
    assert " ".join(generated) == expected
