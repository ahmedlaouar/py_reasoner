save_dag_to_file <- function(graph, filename) {
  # Open the file for writing
  file <- file(filename, "w")
  # Loop through each node in the graph
  for (node in node_labels) {
    children_list <- random_dag$node[[node]]$children
    
    children_str <- ifelse(length(children_list) > 0, paste(children_list, collapse = " "), "")

    # Write the line to the file
    writeLines(paste(node, children_str), file)
  }
  # Close the file
  close(file)
}

if(!requireNamespace("bnlearn", quietly = TRUE)) {
  install.packages("bnlearn")
}
library(bnlearn)

# Set the number of nodes in the graph
num_nodes <- 100 - 1

# Generate node labels
node_labels <- paste0(0:num_nodes)

# Generate a random DAG
# nodes: list of nodes. method (used algorithm): ordered (similar to randomDAG of pcalg python), ic-dag, melancon. prob: for ordered algo, probability of each arc burn.in: number of iterations for ic-dag and melancon.   
probabilities <- seq(0.1, 1, by = 0.1)

for (prob in probabilities) {
  random_dag <- random.graph(nodes = node_labels, method= "ordered", prob = prob)
  # random_dag <- random.graph(nodes = node_labels, method= "melancon")
  # random_dag <- random.graph(nodes = node_labels, method = "ic-dag")

  file_name = sprintf("bench_prepa/DAGs/DAGs_with_bnlearn/ordered_method/pos100/prob_%.1f.txt", prob)
  
  save_dag_to_file(random_dag, file_name)
}
