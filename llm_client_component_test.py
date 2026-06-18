from llm_client import generate_response


def main():
    

    response = generate_response("voc-777460345126677478748569bc05e493bdd9.29426320", "What was Apollo 11?", "", [])
    print(response)

if __name__ == "__main__":
    main()