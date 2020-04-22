import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs -- ✅
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Alow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Alow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # @TODO: Use the after_request decorator to set Access-Control-Allow -- ✅

    @app.route('/')
    def index():
        return jsonify({'message': 'Hello'})

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories. -- ✅
    '''
    @app.route('/categories', methods=['GET'])
    def get_category():
        # get all categories
        categories = Category.query.order_by(Category.id).all()

        return jsonify({
            'success': True,
            'categories': [category.format() for category in categories],
        })

        '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. -- ✅
    '''
    @app.route('/questions', methods=['GET'])
    def get_question():
        # get all categories and questions

        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        category_l = [category.format() for category in categories]
        print(category_l)
        # print(questions)

        # paginate
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        q_l = [question.format() for question in questions]
        current_questions = q_l[start:end]
        total_questions = len(Question.query.all())

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': total_questions,
            'categories': category_l,
            'current_category': [current_question['category'] for current_question in current_questions]
        })

        '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. -- ✅
    '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        # get question
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        try:
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            if question is None:
                abort(404)
            else:
                abort(422)

        '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab. -- ✅
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        # init question to be inserted
        d = request.get_json()
        question = d.get('question')
        answer = d.get('answer')
        category = d.get('category')
        difficulty = d.get('difficulty')

        try:
            question = Question(question=question, answer=answer,
                                difficulty=difficulty, category=category)
            question.insert()
            total = len(Question.query.all())
            print(question)
            return jsonify({
                'success': True,
                'total_questions': total,
                'created': question.id
            })

        except Exception:
            abort(422)

        '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start. -- ✅
    '''
    @app.route('/questions/search', methods=['POST'])
    def search():
        term = request.get_json().get('searchTerm', None)
        try:
            questions = Question.query.filter(
                Question.question.ilike("%" + term + "%")).all()
            return jsonify({
                'success': True,
                'questions': [question.format() for question in questions],
                'total_questions': len(questions)
            })
        except Exception:
            abort(422)

        '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def find_category(category_id):
        try:
            questions = Question.query.filter_by(category=category_id).all()
            if len(questions) == 0:
                abort(404)
            return jsonify({
                'questions': [
                    question.format() for question in questions
                ],
                'total_questions': len(questions)
            })
        except Exception:
            abort(404)

        '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=['POST'])
    def quiz():

        # set up quiz
        d = request.get_json()
        previous_question = d['previous_questions']
        print(previous_question)
        q_category = d['quiz_category']['id']
        print(q_category)

        # get questions by category
        if q_category:
            questions = Question.query.filter_by(
                category=str(q_category)).all()
        else:
            questions = Question.query.all()

        remaining_question = []
        listed_questions = [question.format() for question in questions]

        # append question to remaining question list
        for listed_question in listed_questions:
            if listed_question['id'] not in previous_question:
                remaining_question.append(listed_question)

        if len(remaining_question) == 0:
            return jsonify({
                'success': True,
                'question': None
            })

        else:
            r_question = random.choice(remaining_question)
            return jsonify({
                'success': True,
                'question': r_question
            })
        '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''

    # error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            "error": 404,
            "message": "not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            "error": 500,
            "message": "Internal server error"
        }), 500

    return app
