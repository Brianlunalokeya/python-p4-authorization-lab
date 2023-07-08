from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class ClearSession(Resource):
    def delete(self):
        session.clear()
        return {}, 204

class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return make_response(jsonify(articles), 200)

class ShowArticle(Resource):
    def get(self, id):
        article = Article.query.filter_by(id=id).first()
        if not session.get('user_id'):
            return {'message': 'Unauthorized access'}, 401
        elif article.is_member_only:
            return article.to_dict(), 200
        else:
            return {'message': 'Unauthorized access'}, 401

class Login(Resource):
    def post(self):
        username = request.get_json().get('username')
        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            return user.to_dict(), 200
        else:
            return {}, 401

class Logout(Resource):
    def delete(self):
        session.pop('user_id', None)
        return {}, 204

class CheckSession(Resource):
    def get(self):
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
            return user.to_dict(), 200
        else:
            return {}, 401

class MemberOnlyIndex(Resource):
    def get(self):
        if not session.get('user_id'):
            return {'message': 'Unauthorized access'}, 401
        else:
            member_articles = [article.to_dict() for article in Article.query.filter_by(is_member_only=True).all()]
            return make_response(jsonify(member_articles), 200)

class MemberOnlyArticle(Resource):
    def get(self, id):
        if not session.get('user_id'):
            return {'message': 'Unauthorized access'}, 401
        else:
            article = Article.query.filter_by(id=id, is_member_only=True).first()
            if article:
                return article.to_dict(), 200
            else:
                return {'message': 'Article not found'}, 404

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(MemberOnlyIndex, '/members_only_articles')
api.add_resource(MemberOnlyArticle, '/members_only_articles/<int:id>')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
