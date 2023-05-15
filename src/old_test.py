from dl_lite.axiom import Axiom, Modifier, Side
from dl_lite.assertion import assertion
from dl_lite.abox import ABox
from dl_lite.tbox import TBox
from dl_lite.repair import conflict_set
sideB1 = Side("B1",[Modifier.negation])
sideB2 = Side("B2")
sideRn = Side("R",[Modifier.negation,Modifier.projection,Modifier.inversion])
sideR = Side("R",[Modifier.projection,Modifier.inversion])
axiomN = Axiom(sideR,sideB1)
axiomP = Axiom(sideB2,sideR)
tb1 = TBox()
tb1.add_axiom(axiomN)
tb1.add_axiom(axiomP)
tb1.negative_closure()
print(tb1)
#Concepts
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
axioms1 = [ax3,ax4,ax6,ax2]
#TBOX
tbox1 = TBox()
for axiom in axioms1:
    tbox1.add_axiom(axiom)
print(tbox1)
tbox1.negative_closure()
#print(tbox1)
# test 2
#axioms2 = [ax1,ax3]
#tbox2 = TBox(axioms2)
#print(tbox2)
#tbox2.negative_closure()
#print(tbox2)

#Assertions 
ass1 = assertion(man,mark)
ass2 = assertion(eats,mark,ch1)
ass3 = assertion(man,bill)
ass4 = assertion(chicken,mark)
ass5 = assertion(eats,mark,bill)
ass6 = assertion(eats,ch1,ch2)
ass7 = assertion(chicken,ch1)
ass8 = assertion(chicken,ch2)
#assertions = [ass1, ass3, ass4, ass5, ass6, ass7, ass8]
abox = ABox()
abox .add_assertion(ass1)
abox .add_assertion(ass3)
abox .add_assertion(ass4)
abox .add_assertion(ass5)
abox .add_assertion(ass6)
abox .add_assertion(ass7)
abox .add_assertion(ass8)
assertions_list = abox.get_assertions()
for ass in assertions_list:
    print(ass)
conflict_set = conflict_set(tbox1,abox)
for conf in conflict_set :
    print("Axiom : ", conf[0], " | Conflict : (", conf[1], ", ", conf[2],")")
