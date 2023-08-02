import pickle5 as pickle
import os
import pymongo
import urllib.parse


class DB(object):
    def __init__(self):
        self.dataset_dir = os.path.join(os.getcwd(), "dataset")

    def load_done_list(self):
        done_list_file = os.path.join(self.dataset_dir, "done", "done.pkl")
        try:
            with open(done_list_file, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return []

    def save_to_done_list(self, video_path):
        done_list_dir = os.path.join(self.dataset_dir, "done")
        try:
            os.mkdir(done_list_dir)
        except FileExistsError:
            pass
        done_list = self.load_done_list()
        done_list.append(video_path)
        done_list_file = os.path.join(done_list_dir, "done.pkl")
        with open(done_list_file, 'wb') as f:
            pickle.dump(done_list, f)

    def is_already_done(self, video_path):
        done_list = self.load_done_list()
        return video_path in done_list

    def save_dataset_of_specific_leader(self, obj, leader_name):
        leader_dataset_dir = os.path.join(self.dataset_dir, leader_name)
        try:
            os.mkdir(leader_dataset_dir)
        except FileExistsError:
            pass
        dataset_file = os.path.join(leader_dataset_dir, f"{leader_name}.pkl")
        with open(dataset_file, 'wb') as f:
            pickle.dump(obj, f)

    def load_dataset_specific_leader(self, leader_name):
        dataset_file = os.path.join(self.dataset_dir, leader_name, f"{leader_name}.pkl")
        try:
            with open(dataset_file, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return {}

    def load_all_dataset(self):
        leader_names = next(os.walk(self.dataset_dir, (None, [], None)))[1]
        all_dataset = {leader_name: self.load_dataset_specific_leader(leader_name) for leader_name in leader_names}
        return all_dataset

    def merge_with_existing_dataset(self, new_dataset, leader_name, save=True):
        existing_data_set = self.load_dataset_specific_leader(leader_name)
        dataset = {}
        for d in [new_dataset, existing_data_set]:
            for key, value in d.items():
                cur_dataset = dataset.get(key, [])
                cur_dataset.extend(value)
                dataset[key] = cur_dataset
        if save:
            self.save_dataset_of_specific_leader(dataset, leader_name)
        return dataset


class DB2(object):
    """Using Mongo DB"""
    def __init__(self):
        # access os only to specific IPs. Add to permitted ip list here:
        # https://cloud.mongodb.com/v2/634aa2f39be09b2d459ba081#security/network/accessList
        # right now access is allowed from all IPs
        self._mongo_username = "nadavgo"
        self._mongo_password = urllib.parse.quote_plus("FU@Fs3j9d3YTfye")
        self._db_name = "nadav"
        self._collection_name = "leaders_videos"  # collection in mongo is equivalent to a table in sql
        self._connection = None

    def _get_connection(self):
        if self._connection is not None:
            return self._connection
        client = pymongo.MongoClient(
            f"mongodb+srv://{self._mongo_username}:{self._mongo_password}@nadavgo.mkerdcl.mongodb.net/?retryWrites=true&w=majority")
        db = client[self._db_name]
        self._connection = db
        return db

    def build_document(self, name, job_id, video_id):
        return {"name": name, "rev_job_id": job_id, "video_id": video_id}

    def insert_document(self, document):
        """document is of shape: {"name": str, "rev_job_id": str, "video_id": str}"""
        print(f"Started inserting document: {document}")
        db = self._get_connection()
        db[self._collection_name].insert_one(document)
        print(f"Finished inserting document: {document}")

    def get_documents(self, query=None):
        db = self._get_connection()
        return db[self._collection_name].find(query)

    def does_exist(self, query):
        return len(list(self.get_documents(query))) >= 1


if __name__ == '__main__':
    # db = DB()
    # a = db.load_dataset_specific_leader("trump")
    # b = 1

    db = DB2()
    docs = db.get_documents({"name": "trump"})
    for doc in docs:
        print(doc)
