from old_codes.abox import ABox
from dl_lite.assertion import assertion
from dl_lite.axiom import Axiom, Modifier
from dl_lite.tbox import TBox
import threading
import concurrent.futures

def same_individuals(axiom: Axiom, assertion_1: assertion, assertion_2: assertion):
    
    # Check if assertions match with axiom sides
    if (assertion_1.get_assertion_name() == axiom.get_left_side().get_name() and assertion_2.get_assertion_name() == axiom.get_right_side().get_name()):  
        # Check if both assertions are concepts or both are roles and compare individuals
        if assertion_1.is_role() == assertion_2.is_role() and assertion_1.get_individuals() == assertion_2.get_individuals():
            return True
        
        # Check if assertion_1 is role and assertion_2 is concept
        if assertion_1.is_role():
            if Modifier.projection in axiom.get_left_side().get_modifiers():
                
                if Modifier.inversion in axiom.get_left_side().get_modifiers() and \
                        assertion_1.get_individuals()[1] == assertion_2.get_individuals()[0]:
                    return True
                if Modifier.inversion not in axiom.get_left_side().get_modifiers() and assertion_1.get_individuals()[0] == assertion_2.get_individuals()[0]:
                    return True
                
        # Check if assertion_1 is concept and assertion_2 is role
        if assertion_2.is_role():
            if Modifier.projection in axiom.get_right_side().get_modifiers():
                
                if Modifier.inversion in axiom.get_right_side().get_modifiers() and \
                        assertion_1.get_individuals()[0] == assertion_2.get_individuals()[1]:
                    return True
                if Modifier.inversion not in axiom.get_right_side().get_modifiers() and assertion_1.get_individuals()[0] == assertion_2.get_individuals()[0]:
                    return True

def conflict_set(tbox: TBox, abox : ABox) -> list():
        print("------------ Computation of conflicts set -----------")
        conflicts = []
        assertions = abox.get_assertions()
        #tbox.negative_closure()
        negative_axioms = tbox.get_negative_axioms()
        # Browse all negative axioms
        counter = 1
        for axiom in negative_axioms:
            print(f"Axiom number = {counter}")
            # Browse all assertions
            for assertion_1 in assertions:
                # Browse all assertions after the current assertion (to avoid duplicate verifications)
                for assertion_2 in assertions[assertions.index(assertion_1):] :
                    # replace the following call for a function in assertion to compare the individuals 
                    if same_individuals(axiom, assertion_1, assertion_2) or same_individuals(axiom, assertion_2, assertion_1):
                        conflicts.append((axiom, assertion_1, assertion_2))
                        print(f"Axiom {counter}: {axiom} | Conflict: ({assertion_1}, {assertion_2})")
            counter += 1
        return conflicts


def supports_deduction(find_assertion: assertion, positive_axioms: list(), abox: ABox):
    supports = []
    for axiom in positive_axioms:
        if axiom.get_right_side().get_name() == find_assertion.get_assertion_name() :
            if find_assertion.is_role():
                new = assertion(axiom.get_left_side().get_name(), find_assertion.get_individuals()[0], find_assertion.get_individuals()[1])
            else:
                new = assertion(axiom.get_left_side().get_name(), find_assertion.get_individuals()[0])
            for abox_assertion in abox.get_assertions():
                if new.get_assertion_name() == abox_assertion.get_assertion_name() and new.get_individuals() == abox_assertion.get_individuals() :
                    supports.append(abox_assertion)
            supports += supports_deduction(new, positive_axioms, abox)
    return supports

def compute_supports(target_assertion: assertion, positive_axioms: list(), abox: ABox):
    supports = supports_deduction(target_assertion, positive_axioms, abox)
    for abox_assertion in abox.get_assertions():
        if target_assertion.get_assertion_name() == abox_assertion.get_assertion_name() and target_assertion.get_individuals() == abox_assertion.get_individuals():
            supports.append(abox_assertion)
    return supports

def check_all_dominance(abox, conflicts, supports):
    for conflict in conflicts:
        conflict_supported = False
        for support in supports:
            if abox.is_strictly_preferred(support, conflict[1]) or abox.is_strictly_preferred(support, conflict[2]):
                conflict_supported = True
                break
        if not conflict_supported:
            return False
    return True

def check_assertion_in_cpi_repair(abox, tbox, check_assertion):
    tbox.negative_closure()
    conflicts = conflict_set(tbox,abox)
    supports = compute_supports(check_assertion, tbox.get_positive_axioms(),abox)
    if check_all_dominance(abox, conflicts, supports):
        print(f"{check_assertion} is in the Cpi-repair of the abox")

def process_axiom(axiom, assertions, conflicts, counter):
    
    for assertion_1 in assertions:
        for assertion_2 in assertions[assertions.index(assertion_1):]:
            if same_individuals(axiom, assertion_1, assertion_2) or same_individuals(axiom, assertion_2, assertion_1):
                conflicts.append((axiom, assertion_1, assertion_2))
                #print(f"Axiom {counter}: {axiom} | Conflict: ({assertion_1}, {assertion_2})")
    print(f"Axiom number {counter} done.")

def conflict_set_with_threads(tbox: TBox, abox: ABox) -> list:
    print("------------ Computation of conflicts set -----------")
    conflicts = []
    assertions = abox.get_assertions()
    negative_axioms = tbox.get_negative_axioms()

    threads = []
    counter = 1
    for axiom in negative_axioms:
        t = threading.Thread(target=process_axiom, args=(axiom, assertions, conflicts, counter))
        t.start()
        threads.append(t)
        counter += 1

    # Wait for all threads to finish
    for t in threads:
        t.join()

    return conflicts


# using ProcessPoolExecutor instead of a ThreadPoolExecutor. useful comment "although we may have multiple threads in a ThreadPoolExecutor, only one thread can execute at a time."
# This function with ProcessPoolExecutor does not work because processes can't share memory, but here I need to make them append to the same conflicts list.
# It works with ThreadPoolExecutor but it does the same thing as in conflict_set_with_threads.
def conflict_set_concurrent_futures(tbox: TBox, abox: ABox) -> list:
    print("---------- Computation of conflicts set ----------")
    conflicts = []
    assertions = abox.get_assertions()
    negative_axioms = tbox.get_negative_axioms()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        counter = 1
        futures = []
        for axiom in negative_axioms:
            future = executor.submit(process_axiom, axiom, assertions, conflicts, counter)
            futures.append(future)
            counter += 1

        # Wait for all futures to complete
        concurrent.futures.wait(futures)

    return conflicts