var gulp = require('gulp');

//include plugins
var changed = require('gulp-changed'),
	scss = require('gulp-sass'),
	plumber = require('gulp-plumber'),
	autoprefixer = require('gulp-autoprefixer'),
	concat = require('gulp-concat'),
	browserSync = require('browser-sync').create(),
	reload = browserSync.reload;

// set paths
// var SRC = 'static';
var SRC_FILES = 'static/**/*';
var SRC_SCSS = 'static/sass/style/*.scss';
var SRC_ALL_SCSS = 'static/sass/**/*.scss';

// distribution
var SRC_DIST_CSS = 'static/css';
// var SRC_DIST_JS = 'static/dist/js';
var SRC_DIST = 'static/dist/';


gulp.task('serve', ['watch'], function(){
	browserSync.init(null, {
		proxy: "http://localhost:8000/en/person/1/",
        files: [SRC_FILES],
        browser: "google chrome",
        port: 7000,
	});
	gulp.watch(SRC_ALL_SCSS, ['scss']);
	// gulp.watch('/templates/*').on('change', reload);
	// gulp.watch('views/*.html').on('change', reload);
	gulp.watch(SRC_DIST_CSS).on('change', reload);		//when there is a change to the css file, reload the page
});

// CASCADE STYLE SHEETS
gulp.task('scss', function(){
	gulp.src(SRC_SCSS)							// set the destination of the scss source file
	.pipe(plumber())
	.pipe(scss())
	.pipe(autoprefixer('last 2 versions'))		// set the css autoprefix to scss, like bourbon
	.pipe(gulp.dest(SRC_DIST_CSS));
	console.log(SRC_DIST_CSS+': done');
												//set the destination of the newly generatede css file
});



gulp.task('watch', function(){					// watch come in the gulp utility, no need to npm install
	// gulp.watch(SRC_ALL_SCSS, ['scss']);
	gulp.watch(SRC_ALL_SCSS, ['scss']);
});


//run the gulp tasks
gulp.task('default', ['serve', 'watch']);
// gulp.task('default', ['watch']);
