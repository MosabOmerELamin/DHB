odoo.define('dhb_custom.website_video_access', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');

    publicWidget.registry.websiteVideoAccess = publicWidget.Widget.extend({
        selector: '[data-slide-id][data-course-id]', // Adjusted selector
        events: {
            'click': '_onVideoAccess',
        },

        _onVideoAccess: function (ev) {
            var $target = $(ev.currentTarget);

            // Logging the event to ensure this function is called
            console.log('Video access event triggered');

            // Suppose `data-slide-id` and `data-course-id` are attributes in your element
            var slideId = $target.data('slide-id');
            var courseId = $target.data('course-id');

            // Logging the slideId and courseId to inspect their values
            console.log('slideId:', slideId, 'courseId:', courseId);

            // Make an AJAX call to your server-side handler
            ajax.jsonRpc("/video/access", 'call', {
                slide_id: slideId,
                course_id: courseId,
            }).then(function (response) {
                // Log the response from the server
                console.log('Server response:', response);
            }).catch(function (error) {
                // Log any error that occurs during the AJAX call
                console.log('AJAX call error:', error);
            });
        },
    });
});
