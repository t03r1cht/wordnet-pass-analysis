import mongo
import helper


def main():
    total = 0
    for name in mongo.db.list_collection_names():
        if not name.startswith("passwords_"):
            continue
        count = mongo.db.get_collection(name).count()
        total += count
        print(helper.format_number(count), "\t\t", name)
    print("Total", helper.format_number(total))


if __name__ == "__main__":
    main()
