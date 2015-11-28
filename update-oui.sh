#!/bin/sh

wget -q http://standards-oui.ieee.org/oui.txt -O -  |\
    grep hex |\
    sed s/\(hex\)// |\
    sed s/Co.//gi |\
    sed s/ltd//gi |\
    sed s/inc//gi|\
    sed s/b.v.//gi |\
    sed s/llc//gi |\
    sed s/"LLC, a Lenovo pany"//gi |\
    sed s/p.//gi |\
    sed s/gmbh//gi |\
    sed s/"+ KG"//gi |\
    sed s/\ [,.]// |\
    sed s/", S.L."//gi |\
    sed s/" \."//g |\
    sed s/[,.]\ *//  |\
    sed s/-/:/ |\
    sed s/-/:/ >> oui.processed
