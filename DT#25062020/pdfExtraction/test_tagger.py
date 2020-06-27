import math
import random
import re
import unittest
from collections import Counter

from implementations.pdf_reader_impl import PdfImpl
from utils import pdf_impl_utils as testables


class TestListDetection(unittest.TestCase):
    def setUp(self):
        # all strings should return ordered/unordered lists
        self.test_strings_for_list = [
            "1. hello",
            "(2) the arithmetic mean (rounded if necessary to the fifth decimal place, with",
            "1. Our clear focus on revenue growth, cost savings, and improved asset utilisation supports our free cash flow cash generation.",
            "2). qwer..",
            "(3). uiop..",
            "c) at any time in any other circumstances falling within Article 3(2) of the Prospectus Directive,",
            "4b) asdf...",
            "5(c) No compromise",
            "(II) 1234;asdfzxcv..",
            "(iv) 324099-fasdvdabf9043r-q0r",
            "xi. 807bdslkaf..",
            # TODO failing strings to be fixed
            # "(i) if \"Actual/Actual (ISDA)\" or \"Actual/Actual\" is specified",
            # "(vii) if \"30E/360 (ISDA)\" is specified in the applicable Final Terms, the number of days in ..",
            # "(a) a dividend (or any distribution from reserves) was declared payable in the general meeting",
            # "6.9 If this Condition 6.9 (Regulatory Call) is specified in the relevant Final Terms as ",
            # "6.3 The undated Notes are perpetual securities in respect",
            # "1.2 Unless previously redeemed, or purchased and cancelled, each"
            # Taken from vodafone report
            # EN DASH {2}
            "–– Free cash flow (‘FCF’) pre-spectrum was €5.4 billion in...",
            # BULLET
            "• Title of the notes: 2.905% Fixed/Floating Rate Notes due 2023",
            # HYPHEN
            "‐ Hello",
            # FIGURE DASH
            "‒ Hello",
            # NON-BREAKING HYPHEN
            "‑ Howdy",
            # BLACK CIRCLE
            "● Excuse me",
            # BLACK SMALL SQUARE
            "▪ Howdy",
            # Taken from bmo with bullets changed.
            # BLACK DIAMOND MINUS WHITE X
            "❖ any of the reforms or pressures described above or any other changes to a relevant interest rate",
            # HEAVY CHECK MARK
            "✔ if LIBOR, EURIBOR or the relevant benchmark rate is discontinued, then the rate of interest on the Notes",
            # taken from lists file from mam
            " xyz",
            # unsupported bullet type(right-pointed arrow) from docx file from mam
            " Nilima",
            # Empty square (un supported view)
            " Good luck",
        ]

        # Normal strings that should not be considered as lists
        self.neg_list = [
            "1 Once upon a time",
            "$13,00,000 fully payable as tax remittance",
            "Associations > asset classes",
            "(a  société anonyme  incorporated in France)",
            "(the \" Second Step-up Date \"), at an interest rate  per annum  which will be subject to a reset every five years and"
            " shall be equal to the sum of the Reference Rate of the relevant Reset Period and the Relevant Margin",
            "(the \" First Step-up Rate \"), payable annually in arrear on 30 April of each year, commencing on 30 April 2025 and"
            " ending on the Second Step-up Date; and",
            "Paris.  Such admission to trading are expected to occur as of the Issue Date or as soon as practicable thereafter.",
            "(the) xsdfoij",
        ]
        return super().setUp()


    # Positive testing
    def test_ord_unord(self):
        for test_str in self.test_strings_for_list:
            # to keep track of tested string in loop
            with self.subTest(test_str=test_str):
                # Send text to determine it's validity as a list
                self.assertEqual(
                    testables.ord_unord_1(test_str), PdfImpl.NAME_LIST,
                    msg=f"Test did not return '{PdfImpl.NAME_LIST}'")


    # Negative testing
    def test_neg_ord_unord(self):
        for neg_str in self.neg_list:
            with self.subTest(test_str=neg_str):
                # check if nan is returned 
                self.assertTrue(
                    math.isnan(testables.ord_unord_1(neg_str)),
                    msg="Did not return nan"
                )


if __name__ == '__main__':
    unittest.main()
