
var imageApp = angular.module('ImageApp', []);
imageApp.controller('ImageController', ['$scope', '$http', function($scope, $http) {
    $scope.sendGoBack = function() {
	$http({
	    url: '/amt.png',
	    method: "GET",
	    params: {
		goback: $scope.goback,
		interval: $scope.interval
	    }
	}).then(function(data, status, headers, config) {
	    $scope.ImageResponse = data;
	}, function (response) {
	    $scope.ImageResponse = response;
	})
    }
}])
