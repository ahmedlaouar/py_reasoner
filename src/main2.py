from repair.owl_cpi_repair import compute_cpi_repair
from repair.owl_cpi_repair_enhanced import compute_cpi_repair_enhanced
from repair.owl_pi_repair import compute_pi_repair
from repair.utils import add_pos_to_db

if __name__ == "__main__":

    ontology_path = "ontologies/univ-bench/lubm-ex-20_disjoint.owl"
    
    #data_path = "bench_prepa/dataset.0.2/University5_p_0.0005.db"

    data_paths = ["bench_prepa/dataset.01/University0_p_0.0005.db", "bench_prepa/dataset.01/University0_p_0.001.db", "bench_prepa/dataset.01/University0_p_0.005.db"] # , "bench_prepa/dataset.01/University0_p_0.00015.db"

    results_path = "bench_prepa/dataset.01/execution_results_0.3.txt"

    relative_path = "bench_prepa/DAGs/DAGs_direct_method/"
    # pos_dir_paths = ["pos1000/", "pos2500/", "pos5000/", "pos750/", "pos500/"] # 

    pos_list = ["pos10000.txt"] #, "pos10000_prob_0.75.txt" 
    
    for data_path in data_paths:

        #for pos_dir_path in pos_dir_paths:
            
            for pos in pos_list:
                try: 
                    pos_path = relative_path + pos

                    add_pos_to_db(data_path, pos_path)

                    results1 = compute_pi_repair(ontology_path,data_path,pos_path)

                    results2 = compute_cpi_repair(ontology_path,data_path,pos_path)

                    results3 = compute_cpi_repair_enhanced(ontology_path,data_path,pos_path)

                    pos_name = pos_path.split("/")[-2] +"_"+ pos_path.split("/")[-1]
                    ABox_name = data_path.split("/")[-1]
                    TBox_name = ontology_path.split("/")[-1]

                    result = results1 + results2 + results3
                    
                    result_str = str(ABox_name)+","+str(TBox_name)+","+str(pos_name)+","
                    
                    result_str += ",".join(str(e) for e in result)

                    with open(results_path, 'a') as file:
                        file.write('\n')
                        file.write(result_str)
                except FileNotFoundError as e:
                    print(f"File {pos_path} not found!")
                    continue
