
list_strings = [("http://dbpedia.org/ontology/Company", "http://dbpedia.org/resource/Bavarian_Brewing_Company__Bavarian_Brewing_Company__1"), 
                ("http://dbpedia.org/ontology/Legislature", "http://dbpedia.org/resource/City_of_Maribyrnong__City_of_Maribyrnong__1"), 
                ("http://dbpedia.org/ontology/Settlement", "http://dbpedia.org/resource/South_Ayrshire__South_Ayrshire__1"),
                ("http://dbpedia.org/ontology/Town", "http://dbpedia.org/resource/Chintamani,_Karnataka__Chintamani__1")]


def clean_data(filepath):

    print(f"cleaning file: {filepath.split("/")[-1]}.")

    with open(filepath, "r") as f:
        lines = f.readlines()

    with open(filepath, "w") as f:
        for line in lines:
            if all(string1 not in line or string2 not in line for string1,string2 in list_strings):
                f.write(line)


if __name__ == "__main__":
    
    print("cleaning data.")
        
    for filepath in ["dataset_preparation/instance_types_lhd_dbo_en_with_timestamps.csv", "dataset_preparation/instance-types_lang=en_specific_with_timestamps.csv"]:
        clean_data(filepath)

    print("Done cleaning data.")