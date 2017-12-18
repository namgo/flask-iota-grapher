
var imageApp = angular.module('ImageApp', []);
imageApp.controller('ImageController', ['$scope', '$http', function($scope, $http) {
    $scope.goback = 1440;
    $scope.interval_back = 3600;
    $scope.sendGoBack = function() {
	$scope.amt_url = "/amt.png?goback="+$scope.goback+"&interval="+$scope.interval_back
	$scope.amt_div_transactions = "/amtDivTransactions.png?goback="+$scope.goback+"&interval="+$scope.interval_back
    }
    $scope.sendStartEnd = function() {
	$scope.amt_url = "/amt.png?min="+$scope.min+"&max="+$scope.max
	$scope.amt_url = "/amtDivTransactions.png?min="+$scope.min+"&max="+$scope.max
    }
}])
