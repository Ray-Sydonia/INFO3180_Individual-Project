"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file contains the routes for your application.
"""

import os
from app import app, db
from flask import render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from app.models import Property
from app.forms import PropertyForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Rayna Jarrett")


@app.route('/properties/create', methods=['GET', 'POST'])
def create_property():
    """Display form to add a new property and handle submission."""
    form = PropertyForm()
 
    if form.validate_on_submit():
        # Handle file upload
        photo = form.photo.data
        filename = secure_filename(photo.filename)
 
        upload_path = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_path, exist_ok=True)
        photo.save(os.path.join(upload_path, filename))
 
        # Save property to database
        price_str = str(form.price.data).replace(',', '')
        new_property = Property(
            title=form.title.data,
            description=form.description.data,
            no_of_rooms=form.no_of_rooms.data,
            no_of_bathrooms=form.no_of_bathrooms.data,
            price=price_str,
            property_type=form.property_type.data,
            location=form.location.data,
            photo=filename
        )
 
        db.session.add(new_property)
        db.session.commit()
 
        flash('Property was successfully added!', 'success')
        return redirect(url_for('properties'))
 
    return render_template('create_property.html', form=form)
 
 
@app.route('/properties')
def properties():
    """Display a list of all properties."""
    all_properties = Property.query.all()
    return render_template('properties.html', properties=all_properties)
 
 
@app.route('/properties/<int:propertyid>')
def property_detail(propertyid):
    """Display details for a specific property."""
    prop = Property.query.get_or_404(propertyid)
    return render_template('property_detail.html', property=prop)
 
 
@app.route('/uploads/<filename>')
def get_image(filename):
    """Serve uploaded property images."""
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)


###
# The functions below should be applicable to all Flask apps.
###

# Display Flask WTF errors as Flash messages
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
