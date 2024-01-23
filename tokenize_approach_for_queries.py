def tokenize_query(query):
    # Split the query into tokens
    tokens = query.replace('(', ' ( ').replace(')', ' ) ').split()

    # Remove commas
    tokens = [token for token in tokens if token != ',']

    return tokens

def generate_sql_query(tokens):
    # Initialize variables
    tables = []
    conditions = []

    # Process tokens
    i = 0
    while i < len(tokens):
        if tokens[i] == '(':
            # Start of a condition block
            table = tokens[i - 1]
            conditions.append(tokens[i + 1])
            i += 4  # Skip the entire condition block
        else:
            # Single table case
            table = tokens[i]
            i += 2  # Skip the table and comma

        tables.append(table)

    # Generate SQL query
    if len(tables) == 2:
        join_conditions = f"{tables[0]}.?0={tables[1]}.?0"
        return f"SELECT * FROM {tables[0]} JOIN {tables[1]} ON {join_conditions}"

    return None

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
        print(query)
        tokens = tokenize_query(query)
        print(tokens)
        sql_query = generate_sql_query(tokens)
        print(sql_query)
        if sql_query:
            print(sql_query)

if __name__ == "__main__":
    main()