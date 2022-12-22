#!/bin/bash
python petfinder-data/data_getter.py ;
python petfinder-data/data_cleaner.py ;
python petfinder-data/data_putter.py ;
wait
