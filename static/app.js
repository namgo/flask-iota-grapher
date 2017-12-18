
var imageApp = angular.module('ImageApp', []);
imageApp.controller('ImageController', function($scope, $http) {
    $scope.sendGoBack = function() {
	console.log('sending goback')
	var params = $.param({
	    goback: $scope.goback,
	    interval: $scope.interval
	});
	$http({
	    url: '/amt.png',
	    method: "GET",
	    params: params
	}).then(function(data, status, headers, config) {
	    $scope.ImageResponse = data;
	}, function (response) {
	    $scope.ImageResponse = response;
	})
    }
    
})
