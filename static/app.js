
var imageApp = angular.module('ImageApp', []);
imageApp.controller('ImageController', ['$scope', '$http', function($scope, $http) {
    $scope.goback = 1440;
    $scope.interval_back = 3600;
    $scope.sendGoBack = function() {
	$http({
	    url: '/amt.png',
	    method: "GET",
	    params: {
		goback: $scope.goback,
		interval: $scope.interval_back
	    }
	}).then(function(data, status, headers, config) {
	    $scope.ImageResponse = data;
	}, function (response) {
	    $scope.ImageResponse = response;
	})
    }
}])
