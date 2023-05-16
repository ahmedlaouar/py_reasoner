from dl_lite.abox import ABox
from dl_lite.assertion import assertion
from dl_lite.axiom import Axiom, Modifier
from dl_lite.tbox import TBox
import threading

# here to define a conflict set function that sorts the elements and do a dichotomic search
#  