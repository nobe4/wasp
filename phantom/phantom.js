var page = require('webpage').create();
var env = require('system').env;

var url_base = 'http://server:' + env.WEB_PORT + '/';

var timeout = 5 * 1000; // 5 s

var key = env.ADMIN_KEY;

// Allow phantomjs to use the website
page.settings.userName = env.AUTH_USERNAME;
page.settings.password = env.AUTH_PASSWORD;
page.settings.resourceTimeout = timeout; // 5 seconds until timeout

// Create a secure hash to verify against the admin view.
function generate_admin_key(){
	// Cycle the count to prevent attack, use the 3 last digits of the timestamps
	var count = Math.floor(+ new Date() / 1000) % 1000;
	if (count < 10){
		count = '00' + count;
	} else if (count < 100){
		count = '0' + count;
	}

	// Generate a base64 ( LXXXLXXXLXXX... ) where L is a char of the key and XXX
	// is the current 3-digits count.
	return btoa(key.split('').map(function(a){return a+count;}).join(''));
}


function get_post(){
	var url = url_base + 'get_post/?admin_key=' + generate_admin_key();

	// Open the admin page, and execute the javascript in it
	page.open(url, function(status) {

		if(parseInt(page.plainText) > 0){
			console.log('Found id ' + page.plainText + ' to check...');
			view_post(page.plainText);
		}
	});

	setTimeout(get_post, timeout);
}

function view_post(id){
	var url = url_base + 'check/' + id + '?admin_key=' + generate_admin_key();

	console.log('Checking post ' + id + '...');

	// Mark the post as checked
	page.open(url, 'POST', function(status) {
		console.log('Post ' + id + ' checked !');
	});

	// And open the page
	page.open(url);
}

get_post();
