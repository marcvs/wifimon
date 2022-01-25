"""information about one cell"""

# vim: foldmethod=indent : tw=100
#
# This code is distributed under the MIT License
#
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=logging-not-lazy, logging-format-interpolation

import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import wifitop.logsetup

# from sqlalchemy import Column, Integer, String


logger = logging.getLogger(__name__)

engine = create_engine("sqlite:///wifitop.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
