$(document).ready(function() {


// Utilities

// Check for selected block p children display property
// and set Toggle button text
function changeToggleText($block) {
    if ($block.children('p').css('display') == 'none') {
        $('#buttonToToggle').html('More')
    } else {
        $('#buttonToToggle').html('Less')
    }
}

function changeTextArea() {
    var title = $('.selected').children('h2').html();
    var text = $('.selected').children('p').html();
    $('#TitleArea').focus();
    $('#TitleArea').val(title);
    $('#TextArea').val(text);
}

changeToggleText($('.selected'))

var changeSelection = function($currentElement, $newElement) {

    $currentElement.removeClass('selected');
    $newElement.addClass('selected');
};

// Click handler to select element
// delegate() will attach click event even if created after page load
$('#document').delegate('div','click', function(event) {

    //Prevent event from bubbling up the DOM tree,
    //preventing any parent div from being notified of event
    event.stopPropagation();
    
    //Select element
    $this = $(this);
    changeSelection($('.selected'), $this)
    
    //Change text in text area
    changeTextArea()

    //Update text on toggle button)
    changeToggleText($this)
});


// Button control

$('#buttonToInsertAfter').click(function() {

    //Create div element, with span element,
    //after selected block
    var div = $('<div/>').append('<h2/>').append('<p/>');
    var $current = $('.selected');
    $current.after(div);

    //Select new element
    $newElement = $current.next()
    changeSelection($current, $newElement)

    changeTextArea()
});

$('#buttonToInsertInside').click(function() {

    //Create div element, with span element,
    //inside selected block,
    //after span element
    var div = $('<div/>').prepend('<p/>').prepend('<h2/>');  
    var $current = $('.selected');
    $current.children('p').after(div);

    //Select new element
    $newElement = $current.children('div').first()
    changeSelection($current, $newElement)
    
    //Clear text area
    changeTextArea()
});

$('#buttonToDelete').click(function() {

    //Delete selected element and everything inside
    //Also remove all bound events and jQuery data associated
    var $selected = $('.selected')
    if ( $selected.attr('id') == 'first' ) {
        r = confirm('You are about to delete the Document.')
        if (r == true) {
            deleteDocument()
        }                 
    } else {
        $selected.remove();
        changeTextArea()    
    }
});

$('#buttonToEdit').click(function() {
    
    var $selected = $('.selected');
    var newTitle = $('#TitleArea').val();
    $selected.children('h2').html(newTitle);
    var newText = $('#TextArea').val();
    $selected.children('p').html(newText);
});

// When we click in the button to edit document
// show the buttons to save and delete,
// also the menu to edit.

$('#buttonToEditDocument').click(function() {

    $(this).hide()
    $('#buttonToSaveConfiguration').hide()
    $('#buttonToSaveChanges').show()
    $('#buttonToDeleteDocument').show()
    $('#menu-edition').show()
    changeTextArea()
});

// Change the visibility of blocks

$('#buttonToToggle').click(function() {

    var $selected = $('.selected').children().not('h2')
    $selected.toggle('fast')
    var status = $('#buttonToToggle').html()
    $('#buttonToToggle').html(status == 'Less' ? 'More' : 'Less')
});

// Ajax calls

function get_id_from_url(url_string) {
    var url_list = url_string.split('')
    var len = url_list.length
    var id_list = []
    for (var i=len-1; i>0; i--) {
        if (url_list[i] == '/') {
            break
        } else {
            id_list.push(url_list[i])
        }
    }
    return id_list.reverse().join('')
}

// /save
$('#buttonToSaveDocument').click(function() {

    var $name = $('.name').html();
    var $document = $('#document').html();
                
    $.ajax({
        type: 'POST', 
        url: '/save',
        data: { name: $name, document: $document },
        success: function() {
             //don't redirect if document is not saved! Add alert!
             //Redirect to documents page
             window.location.href = '/documents'
        },
    });
});

// /delete
var deleteDocument = function() {

    // Get document id from url
    var url_string = window.location.pathname
    var id_string = get_id_from_url(url_string)

    if (id_string == 'new') {
        window.location.href = '/documents'
    } else {
        $.ajax({
            type: 'POST',
            url: '/delete',
            data: { id: id_string },
            success: function() {
                // Redirect to documents page
                window.location.href = '/documents'
            },
    });
    }  
};

// /edit
$('#buttonToSaveChanges').click(function() {

    // Get document id from url
    var url_string = window.location.pathname
    var id_string = get_id_from_url(url_string)

    // Get new_name and document content
    var $new_name = $('.name').html();
    var $new_document = $('#document').html();
               
    $.ajax({
        type: 'POST', 
        url: '/edit',
        data: { new_name: $new_name, new_document: $new_document, id: id_string },
        success: function() {
             // Redirect to documents page
             window.location.href = '/documents'
        },
    });   
});

// /configuration

$('#buttonToSaveConfiguration').click(function() {

    // Get document id from url
    var url_string = window.location.pathname
    var id_string = get_id_from_url(url_string)

    // Get new_name and document content
    var $name = $('.name').html();
    var $document = $('#document').html();
               
    $.ajax({
        type: 'POST', 
        url: '/configuration',
        data: { name: $name, document: $document, id: id_string },
        success: function() {
             // Redirect to documents page
             window.location.href = '/documents'
        },
    });   
});


});


