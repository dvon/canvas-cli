#!/bin/bash

echo

# chapter_8.txt (python, slides)
echo python3 ../pdpm.py --slides chapter_8.txt
python3 ../pdpm.py --slides chapter_8.txt
echo mv chapter_8.html chapter_8_slides.html
mv chapter_8.html chapter_8_slides.html
echo python3 ../pdpm.py chapter_8.txt
python3 ../pdpm.py chapter_8.txt
echo python3 ../pdpm.py --pdf chapter_8.txt
python3 ../pdpm.py --pdf chapter_8.txt
echo

# turtle.txt (python)
echo python3 ../pdpm.py turtle.txt
python3 ../pdpm.py turtle.txt
echo python3 ../pdpm.py --pdf turtle.txt
python3 ../pdpm.py --pdf turtle.txt
echo

# nested_classes.txt (java)
echo python3 ../pdpm.py nested_classes.txt
python3 ../pdpm.py nested_classes.txt
echo python3 ../pdpm.py --pdf nested_classes.txt
python3 ../pdpm.py --pdf nested_classes.txt
echo

# i1.txt (processing, rubric)
echo python3 ../pdpm.py i1.txt
python3 ../pdpm.py i1.txt
echo python3 ../pdpm.py --pdf i1.txt
python3 ../pdpm.py --pdf i1.txt
echo

# chapter_5_homework.txt (c, rubric)
echo python3 ../pdpm.py chapter_5_homework.txt
python3 ../pdpm.py chapter_5_homework.txt
echo python3 ../pdpm.py --pdf chapter_5_homework.txt
python3 ../pdpm.py --pdf chapter_5_homework.txt
echo
