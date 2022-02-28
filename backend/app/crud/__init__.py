from .crud_user import user
from .crud_follow import follow
from .crud_blog import blog
from .crud_picture import picture
from .crud_thumb import thumb
from .crud_comment import comment

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
