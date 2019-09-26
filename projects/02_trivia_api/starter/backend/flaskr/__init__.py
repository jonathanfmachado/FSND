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
                             'GET,PATCH,POST,DELETE,OPTIONS')
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
        Endpoint to handle DELETE requests for Questions.
        '''
        question = Question.query.filter(
            Question.id == question_id).one_or_none()

        question.delete()

        return jsonify({
            'success': True,
        })

    @app.route('/questions', methods=['GET', 'POST'])
    def get_questions():
        '''
        Endpoint to handle GET and POST requests for Questions.
        '''

        if request.method == 'POST':
            body = request.get_json()

            if body['searchTerm']:
                # SEARCH QUESTION: containing 'searchTerm'
                print(body)
                questions = Question.query.filter(
                    Question.question.contains(body['searchTerm'])).all()
                formatted_questions = [question.format()
                                       for question in questions]
                return jsonify({
                    'success': True,
                    'questions': formatted_questions,
                })

            else:
                # CREATE NEW QUESTION: It will require the question and answer text, category, and difficulty score.
                new_question = Question(
                    question=body['question'], answer=body['answer'], category=body['category'], difficulty=body['difficulty'])
                new_question.insert()
                return jsonify({'success': True, })

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
        Endpoint to handle GET requests for Questions.
        '''
        category = Category.query.filter(
            Category.id == category_id).one_or_none()
        # page = request.args.get('page', 1, type=int)
        # start = (page - 1) * QUESTIONS_PER_PAGE
        # end = start + QUESTIONS_PER_PAGE

        # body = request.get_json()

        questions = Question.query.filter(
            Question.category == category.id).all()
        formatted_questions = [question.format() for question in questions]
        # formatted_questions = formatted_questions[start:end]

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

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

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

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

    return app
