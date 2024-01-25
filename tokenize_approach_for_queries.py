def main():
    # Input queries
    queries = [
        "AAA(?0), BBB(?0)",
        "AAA(?0), RRR(?0, ?_u0)",
        "RRR(?0, ?_u0), AAA(?0)",
        "AAA(?0), RRR(?_u0, ?0)",
        "RRR(?_u0, ?0), AAA(?0)",
        "RRR(?0, ?_u0), PPP(?0, ?_u1)",
        "RRR(?0, ?_u0), PPP(?_u1, ?0)",
        "RRR(?_u0, ?0), PPP(?0, ?_u1)",
        "RRR(?_u0, ?0), PPP(?_u1, ?0)",
        "PPP(?0, ?1), RRR(?0, ?1)",
        "PPP(?0, ?1), RRR(?1, ?0)",
        "PPP(?1, ?0), RRR(?0, ?1)",
        "PPP(?1, ?0), RRR(?1, ?0)",
    ]

    # Generate SQL queries
    for query in queries:        
        # this function generates a sql query from a conjunctive query, it assumes the query to have just 2 atoms
        # it returns the sql_query alongside table names to faciliate construction of conlicts
        query = query.replace(' ', '').replace('),', '), ').split()
        # split query into two sides
        first, second = query[:2]        
        # tokenize each side and remove commas and parenthesis
        first_tokens = [token for token in first.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
        second_tokens= [token for token in second.replace(',', ' , ').replace('(', ' ( ').replace(')', ' ) ').split() if token not in [',', '(', ')']]
        print(first_tokens)
        print(second_tokens)
        # find matching elements between first and second tokens
        matching_indexes = [(i, j) for i, item1 in enumerate(first_tokens[1:]) for j, item2 in enumerate(second_tokens[1:]) if item1 == item2]
        print(matching_indexes)
        # Generate query according to matches
        sql_query = f"SELECT t1.id,t2.id FROM {first_tokens[0]} t1 JOIN {second_tokens[0]} t2 ON"
        for (index0,index1) in matching_indexes:
            sql_query += " t1.individual"+str(index0)+" = t2.individual"+str(index1)+" and"
        # remove last trailing "and"
        sql_query = sql_query.rsplit(' ', 1)[0]
        print(sql_query)
        print("------------------------------------------")

if __name__ == "__main__":
    main()