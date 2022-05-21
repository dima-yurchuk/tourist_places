import unittest
from flask_testing import TestCase
from app import db, create_app

app = create_app()
# app.config.update(FLASK_ENV = 'testing',
#                   SQLALCHEMY_DATABASE_URI='sqlite:///testing.db',
#                   SECRET_KEY='secretkeyfortesting', WTF_CSRF_ENABLED=False,
#                   IMG_STORAGE_URL_DEV='https://res.cloudinary.com/hqnqltror/image/'
#                                   'upload/v1652001437/pictures_dev/',
#                   IMG_STORAGE_FOLDER_DEV='pictures_dev')
from app.user.models import User, Role
from app.tourist_places.models import Category, Region, Place, \
    Comment, Rating, Type
from flask_login import current_user


class BaseTestCase(TestCase):

    def create_app(self):
        app.config.update(FLASK_ENV='testing',
                          SQLALCHEMY_DATABASE_URI='sqlite:///testing.db',
                          WTF_CSRF_ENABLED=False,
                          IMG_STORAGE_URL_DEV='https://res.cloudinary.com/hqnqltror/image/'
                                              'upload/v1652001437/pictures_dev/',
                          IMG_STORAGE_FOLDER_DEV='pictures_dev')
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()
        db.session.add_all([
            Role(name='admin'),
            Role(name='author of post'),
            Role(name='end user'),
            User(username='tester1',
                 email='tester1@gmail.com',
                 password='qwerTy#45',
                 role_id=1,
                 activated=True),
            User(username='tester2',
                 email='tester2@gmail.com',
                 password='qwerTy#45',
                 role_id=2,
                 activated=True),
            User(username='tester3',
                 email='tester3@gmail.com',
                 password='qwerTy#45',
                 role_id=3,
                 activated=True),
            Category(name='Гори'),
            Category(name='Море'),
            Category(name='Зелений туризм'),
            Region(name='Івано-Франківська'),
            Region(name='Київська'),
            Region(name='Одеська'),
            Place(category_id=1, user_id=1, region_id=1, title='Назва місця 1',
                 content='Короткий опис місця 1', location='Ukraine'),
            Place(category_id=2, user_id=2, region_id=2, title='Назва місця 2',
                  content='Короткий опис місця 2', location='Ukraine'),
            Place(category_id=2, user_id=2, region_id=3, title='Назва місця 3',
                  content='Короткий опис місця 3', location='Ukraine')
        ])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

class TestsCRUD(BaseTestCase):
    def test1_create_place_not_auth(self):
        response = self.client.get('/place/create')
        self.assert401(response)

        response = self.client.post('/post/create',
                                    data={'category': 2,
                                          'region': 1,
                                          'title': 'Заголовок місця 5',
                                          'content': 'Короткий опис місця 5',
                                          'location': 'Ukraine'
                                          },
                                    follow_redirects=True)
        self.assertNotEqual(response.status_code, 200)

    def test2_view_place_not_auth(self):
        response = self.client.get('place/1')
        self.assert200(response)
        self.assertTrue(
            f'<h5 class="card-title">Назва місця 1</h5>'
            in response.get_data(as_text=True))

        self.assertTrue('Короткий опис місця 1'
                        in response.get_data(as_text=True))

        self.assertFalse(f'<a href="{{url_for(\'place_bp_in.place_update\', '
                         f'place_id=place.id)}}" class="btn btn-info">'
                         f'Редагувати</a>' in response.get_data(as_text=True))

    def test3_update_place_not_auth(self):
        response = self.client.get('place/1/update')
        self.assert403(response)

        response = self.client.post('place/1/update',
                                    data={'category': 1,
                                          'title': 'Заголовок місця '
                                                   '1(оновлений)',
                                          'content': 'Короткий опис місця '
                                                     '1(оновлений)',
                                          'location': 'Ukraine(оновлено)'},
                                    follow_redirects=True)

        self.assertNotEqual(response.status_code, 200)

    def test4_delete_place_not_auth(self):
         response = self.client.get('place/1/delete')
         self.assert403(response)

# тест успішного створення поста для авторизованого користувача
    def test5_create_post_auth(self):
        with self.client:
            response = self.client.post('/auth/login',
                                        data={'email': 'tester2@gmail.com',
                                              'password': 'qwerTy#45'},
                                        follow_redirects=True)
            self.assert200(response)

            response = self.client.get('/place/create')
            self.assert200(response)

            response = self.client.post('/place/create',
                                        data={'category': 1,
                                              'region': 1,
                                              'title': 'Заголовок місця 6',
                                              'content': 'Короткий опис місця 6',
                                              'location': 'Ukraine'
                                              },
                                        follow_redirects=True)
            self.assert200(response)

            self.assertMessageFlashed('Публікація успішно створена',
                                      category='success')
            self.assertTrue('<h5 class="card-title">Заголовок місця 6</h5>'
                            in response.get_data(as_text=True)
                            )


    def test6_view_place_auth(self):
        with self.client:
            response = self.client.post('/auth/login',
                                        data={'email': 'tester2@gmail.com',
                                              'password': 'qwerTy#45'},
                                        follow_redirects=True)
            self.assert200(response)
            response = self.client.get('place/3')
            self.assert200(response)

            self.assertTrue(
                f'<h5 class="card-title">Назва місця 3</h5>'
                in response.get_data(as_text=True))

            self.assertTrue('Короткий опис місця 3'
                            in response.get_data(as_text=True))

            self.assertTrue('id="favourite_icon" class="bi icons"></a>'
                            in response.get_data(as_text=True))


    def test7_update_place_auth(self):
        with self.client:
            response = self.client.post('/auth/login',
                                        data={'email': 'tester2@gmail.com',
                                              'password': 'qwerTy#45'},
                                        follow_redirects=True)
            self.assert200(response)
            place = Place.query.get_or_404(3)

            response = self.client.get(f'place/3/update')

            if place.user_id == current_user.id:
                self.assert200(response)
            else:
                self.assertNotEqual(response.status_code, 200)


            response = self.client.post('place/1/update',
                                        data={'category': 1,
                                              'title': 'Заголовок місця '
                                                       '3(оновлений)',
                                              'content': 'Короткий опис місця '
                                                         '3(оновлений)',
                                              'location': 'Ukraine(оновлено)'},
                                        follow_redirects=True)

            if place.user_id == current_user.id:
                self.assert200(response)
            else:
                self.assertNotEqual(response.status_code, 200)

    def test8_delete_place_auth(self):
        with self.client:
            response = self.client.post(
                '/auth/login',
                data={'email': 'tester2@gmail.com',
                      'password': 'qwerTy#45'},
                follow_redirects=True)

            place = Place.query.get_or_404(3)

            response = self.client.get(
                f'/place/3/delete', follow_redirects=True)

            if place.user_id == current_user.id:
                self.assert200(response)
                response = self.client.get(f'post/3')
                self.assert404(response)
            else:
                self.assert403(response)

if __name__ == '__main__':
    unittest.main()
