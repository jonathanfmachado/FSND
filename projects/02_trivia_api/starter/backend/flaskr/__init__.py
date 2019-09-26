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

    # Set up CORS. Allow '*' for origins.
    # CORS(app)

    setup_db(app)

    # CORS Headers: Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        '''
        Endpoint to handle GET requests for all available categories.
        '''

        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        return jsonify({
            'success': True,
            'categories': formatted_categories,
            'total_categories': len(formatted_categories)
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        '''
        Endpoint to handle DELETE requests: Questions objects.
        '''
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        if question:
            question.delete()
            return jsonify({
                'success': True,
                'message': 'Question succesfully deleted'
            })

        else:  # Question doesn't exist in the database, return 404
            not_found('Question not found')

    @app.route('/questions', methods=['GET', 'POST'])
    def get_questions():
        '''
        Endpoint to handle GET and POST requests for Questions.
        '''

        if request.method == 'POST':
            body = request.get_json()

            if body['searchTerm']:
                # SEARCH QUESTION: containing 'searchTerm'
                questions = Question.query.filter(
                    Question.question.contains(body['searchTerm'])).all()
                formatted_questions = [question.format()
                                       for question in questions]
                return jsonify({
                    'success': True,
                    'questions': formatted_questions,
                })

            else:
                # Create a new Question
                try:
                    new_question = Question(question=body['question'],
                                            answer=body['answer'],
                                            category=body['category'],
                                            difficulty=body['difficulty'])
                    new_question.insert()
                    return jsonify({'success': True, })
                except:
                    unprocessable(422)

        else:  # GET
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE

            questions = Question.query.all()
            formatted_questions = [question.format() for question in questions]
            formatted_questions = formatted_questions[start:end]

            categories = Category.query.all()
            formatted_categories = [category.format()
                                    for category in categories]

            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'categories': formatted_categories,
                'total_questions': len(questions),
                'current_category': {'id': 1, 'type': 'Science'}
            })

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category_id(category_id):
        '''
          GET endpoint to get questions based on category.
        '''
        category = Category.query.filter(
            Category.id == category_id).one_or_none()
        if not category:
            not_found('Category not found!')

        questions = Question.query.filter(
            Question.category == category.id).all()
        formatted_questions = [question.format() for question in questions]

        # Get all Categories
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'categories': formatted_categories,
            'total_questions': len(formatted_questions),
            'current_category': category.format()
        })

    @app.route('/quizzes', methods=['GET', 'POST'])
    def get_quizzes():
        body = request.get_json()
        given_category_id = body['quiz_category']['id']
        previous_questions = body['previous_questions']
        question = Question.query.filter(
            Question.id.notin_(previous_questions),
            Question.category == given_category_id).first()

        return jsonify({
            'success': True,
            'question': question.format() if question else False,
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    return app
