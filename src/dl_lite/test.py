#Concepts
from axiom import Axiom, Modifier, Side
from tbox import TBox

human = "Human"
man = "Man"
chicken = "Chicken"
#Roles
eats = "Eats"
#Individuals
mark = "Mark"
bill = "Bill"
ch1 = "ch1"
ch2 = "ch2"
#Tbox sides and Axioms
side1 = Side(human)
side1n = Side(human, [Modifier.negation])
side2 = Side(man, [Modifier.negation])
side3 = Side(eats, [Modifier.inversion])
side4 = Side(chicken)
side5 = Side(eats, [Modifier.projection])
side6 = Side(man)
side7 = Side(chicken, [Modifier.negation])
side8 = Side(eats, [Modifier.projection,Modifier.inversion])
#Axioms
ax3 = Axiom(side6,side1)
ax1 = Axiom(side4,side1n)
ax4 = Axiom(side1,side7)
ax5 = Axiom(side6,side7)
ax2 = Axiom(side5,side7)
ax6 = Axiom(side8,side2)

# a tbox with all possible axioms to check conflicts 
# test 1
axioms1 = [ax3,ax4]
#TBOX
tbox1 = TBox(axioms1)
print(tbox1)
tbox1.negative_closure()
print(tbox1)
# test 2
axioms2 = [ax1,ax3]
tbox2 = TBox(axioms2)
print(tbox2)
tbox2.negative_closure()
print(tbox2)