import os
from dotenv import load_dotenv
import redis
from redis.commands.search.field import TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

load_dotenv()

r = redis.Redis(
    host=os.environ["redis_host"],
    port=int(os.environ["redis_port"]),
    password=os.environ["redis_password"],
)

schema = (
    TextField("$.title", as_name="title"),
    NumericField("$.date", as_name="date"),
)
r.ft("articles").create_index(
    schema, definition=IndexDefinition(prefix=["articles:"], index_type=IndexType.JSON)
)
