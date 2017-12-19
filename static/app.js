
var imageApp = angular.module('ImageApp', []);
imageApp.controller('ImageController', ['$scope', '$http', function($scope, $http) {
    $scope.goback = 1440;
    $scope.interval_back = 3600;
    $scope.interval_date = 3600;
    $scope.sendGoBack = function() {
	$scope.amt_url = "/amt.png?goback="+$scope.goback+"&interval="+$scope.interval_back
	$scope.amt_div_transactions = "/amtDivTransactions.png?goback="+$scope.goback+"&interval="+$scope.interval_back
	$http.get('/table.json', {
	    params: {
		goback: $scope.goback,
		interval: $scope.interval_back
	    }
	}).then(function(response) {
	    $scope.tabledata = response.data
	})
	$http.get('/table_per_day.json', {
	    params: {
		goback: $scope.goback,
		interval: $scope.interval_back
	    }
	}).then(function(response) {
	    $scope.tabledata_per_day = response.data
	})
    }
    $scope.sendStartEnd = function() {
	$scope.amt_url = "/amt.png?min="+$scope.min+"&max="+$scope.max+"&interval="+$scope.interval_date
	$scope.amt_div_transactions = "/amtDivTransactions.png?min="+$scope.min+"&max="+$scope.max+"&interval="+$scope.interval_date
	$http.get('/table.json', {
	    params: {
		min: $scope.min,
		max: $scope.max,
		interval: $scope.interval_date
	    }
	}).then(function(response) {
	    $scope.tabledata = response.data
	})
	$http.get('/table_per_day.json', {
	    params: {
		min: $scope.min,
		max: $scope.max,
		interval: $scope.interval_date
	    }
	}).then(function(response) {
	    $scope.tabledata = response.data
	})
    }
    $scope.sendGoBack();
}])
