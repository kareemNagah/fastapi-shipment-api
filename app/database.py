import sqlite3
from pathlib import Path

from .schemas import ShipmentBody, ShipmentPatch, ShipmentStatus

# Path to the database file in the project root (where your DB viewer/SQLTools connects)
DB_PATH = Path(__file__).resolve().parent.parent / "sqlite.db"


class DataBase:
    # def __init__(self):
    #     self.conn = sqlite3.connect(
    #         DB_PATH, check_same_thread=False
    #     )  # run db outside fast api thread
    #     self.cur = self.conn.cursor()
    #     self.create_table()

    def create_connection(self):
        self.conn = sqlite3.connect(
            DB_PATH, check_same_thread=False
        )  # run db outside fast api thread
        self.cur = self.conn.cursor()

    def create_table(self):
        self.cur.execute(
            """
                  CREATE TABLE IF NOT EXISTS shipment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        weight REAL NOT NULL,
                        status TEXT NOT NULL
                  )
            """,
        )
        self.conn.commit()

    def create(self, shipment: ShipmentBody) -> int:
        # get max id from shipment table
        self.cur.execute(
            """
            SELECT COALESCE(MAX(id), 0) FROM shipment 
            """
        )
        result = self.cur.fetchone()

        new_id = result[0] + 1

        # insert values into shipment table

        self.cur.execute(
            """
                INSERT INTO shipment (id, content, weight, status) VALUES (:id, :content, :weight, :status)
            """,
            {
                "id": new_id,
                **shipment.model_dump(),
            },
        )

        self.conn.commit()
        return new_id

    def replace(self, id: int, shipment: ShipmentBody) -> ShipmentStatus:
        self.cur.execute(
            """
            REPLACE INTO shipment (id, content, weight, status) VALUES (:id, :content, :weight, :status)
            """,
            {
                "id": id,
                **shipment.model_dump(),
            },
        )
        self.conn.commit()
        return ShipmentStatus(id=id, **shipment.model_dump())

    def get(self, id: int) -> ShipmentStatus | None:

        self.cur.execute(
            """
            SELECT * FROM shipment WHERE id = ?
            """,
            (id,),
        )
        row = self.cur.fetchone()

        return (
            ShipmentStatus(
                id=row[0],
                content=row[1],
                weight=row[2],
                status=row[3],
            )
            if row
            else None
        )

    # get latest shipment
    def get_latest(self) -> ShipmentStatus:
        self.cur.execute(
            """
            SELECT * FROM shipment WHERE id = (SELECT MAX(id) FROM shipment)
            """
        )
        row = self.cur.fetchone()

        return ShipmentStatus(
            id=row[0],
            content=row[1],
            weight=row[2],
            status=row[3],
        )

    # update shipment
    def update(
        self,
        id: int,
        shipment: ShipmentPatch,
    ) -> ShipmentStatus | None:
        if self.get(id) is None:
            return None

        self.cur.execute(
            """
            UPDATE shipment
            SET content = COALESCE(:content, content),
                weight  = COALESCE(:weight, weight),
                status  = COALESCE(:status, status)
        WHERE id = :id
        """,
            {
                "id": id,
                **shipment.model_dump(mode="json"),
            },
        )

        self.conn.commit()
        return self.get(id)

    def delete(self, id: int) -> bool:
        self.cur.execute(
            """
            DELETE FROM shipment WHERE id = ?
            """,
            (id,),
        )
        self.conn.commit()
        return self.cur.rowcount > 0
    def close(self):
        self.conn.close()


    def __enter__(self):
        self.create_connection()
        self.create_table()
        return self
        
    def __exit__(self, *args):
        self.conn.close()
        
with DataBase() as db :
    print(db.get(1).model_dump_json(indent=2))

