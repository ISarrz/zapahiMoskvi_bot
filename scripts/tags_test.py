

# from modules.database import Category, Placemark, Tag
from modules.database.placemark.category import Category
from modules.database.placemark.tag import Tag
from modules.database import DB
from modules.database.placemark.placemark import Placemark

# category = Category.insert("love")
#
tag = Tag.insert(name="Irochka")
tag.verify()
tag.verify()
tag.verify()
tag.verify()
tag.verify()
tag.verify()
tag.verify()
tag.verify()
# #
# tag.insert_category(category)
# x = category.tags
# tag.delete_category(category)

verified = Tag.get_verified(tag)

# category.delete()
tag.delete()

DB.insert_one(DB.verified_tags_table_name, tag_id=1)
