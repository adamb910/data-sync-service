from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from repository.engine import engine
from repository.models.data_batch import DataBatch


# Could extend with strategy pattern to allow different implementations
class SyncService():
    
    def push_batch(self, id, change, updated_batch):
        synced_batch = None
        match change:
            case "insert":
                synced_batch = self._insert(updated_batch)
            case "delete":
                synced_batch = self._delete(id)
            case "update":
                synced_batch = self._update(id, updated_batch)

        return synced_batch
    
    
    def get_batches_since_datetime(self, datetime):
        session = Session(engine)
        records = session.query(DataBatch).filter(DataBatch.updated_at >= datetime).all()
        print("SyncService.get_batches_since_datetime")
        records_as_dicts = []

        for record in records:
            records_as_dicts.append(record.to_dict())

        return records_as_dicts


    def _insert(self, data):
        with Session(engine) as session:
            batch = DataBatch(data=data, updated_at=datetime.now(), status="active")
            session.add(batch)
            session.commit()
        return batch


    def _delete(self, id):  
        with Session(engine) as session:
            batch_to_delete = session.query(DataBatch).filter(DataBatch.id == id).first()
            if batch_to_delete:
                # this operation could be encapsulated in the object
                batch_to_delete.status = "deleted"
                session.commit()
                return batch_to_delete

    def _update(self, id, data):
        with Session(engine) as session:
            batch_to_update = session.query(DataBatch).filter(DataBatch.id == id).first()
            if batch_to_update:
                batch_to_update.data = data
                batch_to_update.updated_at=datetime.now()
                session.commit()
                return batch_to_update
