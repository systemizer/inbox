'use strict';

/* Controllers */

angular.module('monocleApp.controllers', [])
  .controller('accountsController', ['$scope', '$location', '$timeout', 'monocleAPIservice', function($scope, $location, $timeout, monocleAPIservice) {
      $scope.emailFilter = null;
      $scope.errorFilter = null;
      $scope.providerFilter = null;
      $scope.stateFilter = null;
      $scope.accountsList = [];
      $scope.state_count = {};
      $scope.provider_count = {};
      $scope.predicate = 'id';

      $scope.sort = function (predicate) {
        if($scope.predicate == predicate) {
          $scope.reverse = !$scope.reverse;
        } else {
          $scope.reverse = false;
          $scope.predicate = predicate;
        }
      };

      $scope.select_account = function (account_id) {
        $scope.stopRefresh();
        $location.url("/account/" + account_id);
      };

      $scope.parseAccountResponse = function(response) {
          $scope.accountsList = response['account_info'];
	  response = response['account_info'];
          var i = 0;
          var state_count = {}
          var provider_count = {}
          for(i = 0; i < response.length; i++) {
            if(typeof state_count[response[i].state] == 'undefined')
              state_count[response[i].state] = 0;

            state_count[response[i].state] += 1;

            if(typeof provider_count[response[i].provider] == 'undefined')
              provider_count[response[i].provider] = 0;

            provider_count[response[i].provider] += 1;

            var percent = Math.floor((response[i].local_count/response[i].remote_count) * 100);
            if(percent > 100) {
              percent = 100;
            }

            response[i].percent = percent
          }

          $scope.state_count = state_count;
          $scope.provider_count = provider_count;
      };

      $scope.refreshAccountData = function() {
        monocleAPIservice.getAccounts().success(function (response) {
          $scope.parseAccountResponse(response);
        });
      };

      $scope.refreshAccountData();

      $scope.filterState = function (state) {
        $scope.stateFilter = state;
      };

      $scope.filterProvider = function (provider) {
        $scope.providerFilter = provider;
      };

      $scope.accountFilter = function (account) {
            var keyword = new RegExp($scope.emailFilter, 'i');
            var error_keyword = new RegExp($scope.errorFilter, 'i');
            return (!$scope.emailFilter || keyword.test(account.email)) && 
               (!$scope.providerFilter || account.provider == $scope.providerFilter) &&
               (!$scope.stateFilter || account.state == $scope.stateFilter) &&
               (!$scope.errorFilter || error_keyword.test(account.sync_error));
      };

      $scope.stopRefresh = function() {
        if ($scope.timer) {
          $timeout.cancel($scope.timer);
        }
      };

      $scope.onTimeout = function() {
        $scope.refreshAccountData();
        $scope.timer = $timeout($scope.onTimeout, 3000);
      };
      $scope.timer = $timeout($scope.onTimeout, 3000);

      $scope.$on("$destroy", function() {
        $scope.stopRefresh();
      })

  }])
  .controller('accountController', ['$scope', '$timeout', 'monocleAPIservice', '$routeParams', function($scope, $timeout, monocleAPIservice, $routeParams) {
      $scope.account = {};
      $scope.folders = [];
      $scope.id = $routeParams.id;

      $scope.refreshDetails = function() {
        monocleAPIservice.getAccountDetails($scope.id).success(function (response) {
          if (response.account.provider == 'eas') {
            var i = 0;
            for(i = 0; i < response.folders.length; i++) {
              var rate = Math.floor(response.folders[i].num_downloaded/response.folders[i].download_time);
              rate = (rate === null || isNaN(rate)) ? '' : rate;
              response.folders[i].rate = rate;
            }
          }

          $scope.account = response.account;
          $scope.folders = response.folders;
        });
      };

      $scope.refreshDetails();

      $scope.stopRefresh = function() {
        if ($scope.timer) {
          $timeout.cancel($scope.timer);
        }
      };

      $scope.accountAction = function(action) {
        monocleAPIservice.accountAction($scope.id, action).success(function (response) {
          $scope.account = response.account;
          $scope.folders = response.folders;
        });
      };

      $scope.stopRefresh = function() {
        if ($scope.timer) {
          $timeout.cancel($scope.timer);
        }
      };

      $scope.onTimeout = function() {
        $scope.refreshDetails();
        $scope.timer = $timeout($scope.onTimeout, 3000);
      };

      $scope.timer = $timeout($scope.onTimeout, 3000);

      $scope.$on("$destroy", function() {
        $scope.stopRefresh();
      })

  }]);
