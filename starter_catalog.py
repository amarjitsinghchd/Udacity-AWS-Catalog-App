# Dummy Items created for start up rathe than empty
catalog = [{'name': 'Soccer', 'id': '1', 'user_id': '1'}, 
{'name': 'Baseball', 'id': '2', 'user_id': '2'}]

catalog_item1 = [{'name': 'soccer ball', 'description': 'The soccer ball comes in 3 sizes - kids,' \
'Youth and Adult.', 'catalog_id': '1'}, 
{ 'name': 'Shin Guards', 'description': ' The shin guard is for shin protection', 'catalog_id': '1'},
{'name': 'Cleats', 'description': 'Cleats helps players have good grip', 'catalog_id': '1'}]


# Dummy 2
catalog_item2 = [{'name': 'Base ball bat', 'description': 'The baseball bat comes in different sizes \
- kids, Youth and Adult.' , 'catalog_id': '2'}, 
{ 'name': 'Shin Guards', 'description': ' The shin guard is for shin protection', 'catalog_id': '2'},
{'name': 'Helmet', 'description': 'Helmet is for head protection and must be worm at all times during \
the game', 'catalog_id': '2'}]

catalog_items = [catalog_item1, catalog_item2]

user = [{'name': 'A Singh', 'email': 'aswchd@gmail.com', 'picture': 'https://lh3.googleusercontent.com/-Z_ibn6llwdE/AAAAAAAAAAI/AAAAAAAAAeA/diI-FlrpBC0/photo.jpg'}, 
{'name': 'Amarjit', 'email': 'amarjit_71@hotmail.com', 'picture': 'https://lh3.googleusercontent.com/-Z_ibn6llwdE/AAAAAAAAAAI/AAAAAAAAAeA/diI-FlrpBC0/photo.jpg'}]


if __name__ == '__main__':
	for icatalog in catalog:
		print 'NAME:', icatalog['name']
		print 'id:', icatalog['id']
	
	for iuser in user:	
		print 'user name:', iuser['name']
