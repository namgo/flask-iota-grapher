var graphApp = angular.module('graphApp', []);
graphApp.controller('GraphController', function($scope, $http, $sce) {
    var d = new Date();
    console.log(d.getTime())
    $scope.startTime = d.getTime()-(2000*60);
    $scope.endTime = d.getTime()+1000;
    $scope.groupBySeconds = 30;
    
    $scope.renderHtml = function(html_code)
    {
	return $sce.trustAsHtml(html_code);
    };
    $scope.getSells = function () {
	$http({
	    method: 'GET',
	    url: 'http://'+window.location.hostname+':5000/api/sells?min='+
		$scope.startTime+'&max='+$scope.endTime+'&divideby='+
		$scope.groupBySeconds
	}).then(function(data) {
	    $scope.sellGraph = data.data;
	},function(error) {
	    console.log(error);
	})
    }
})
