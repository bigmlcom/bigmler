import os

from lettuce import world, step

from bigml.api import HTTP_OK, HTTP_UNAUTHORIZED

def check_debug(command):
    """Adds verbosity level and command print.

    """
    debug = os.environ.get('BIGMLER_DEBUG', False)
    verbosity = 0
    if debug:
        verbosity = 1
        print command
    command = "%s --verbosity %s" % (command, verbosity)
    return command

def check_http_code(resources):
    """Checks the http code in the resource list

    """
    if resources['code'] == HTTP_OK:
        assert True
    else:
        assert False, "Response code: %s" % resources['code']

def store_init_resources():
    """Store the initial existing resources grouped by resource_type

    """
    sources = world.api.list_sources()
    if sources['code'] == HTTP_UNAUTHORIZED:
        assert False, ("Unable to list your sources. Please check the"
                       " BigML domain and credentials to be:\n\n%s" %
                       world.api.connection_info())
    check_http_code(sources)
    world.init_sources_count = sources['meta']['total_count']

    datasets = world.api.list_datasets()
    check_http_code(datasets)
    world.init_datasets_count = datasets['meta']['total_count']

    models = world.api.list_models('ensemble=false')
    check_http_code(models)
    world.init_models_count = models['meta']['total_count']

    predictions = world.api.list_predictions()
    check_http_code(predictions)
    world.init_predictions_count = predictions['meta']['total_count']

    evaluations = world.api.list_evaluations()
    check_http_code(evaluations)
    world.init_evaluations_count = evaluations['meta']['total_count']

    ensembles = world.api.list_ensembles()
    check_http_code(ensembles)
    world.init_ensembles_count = ensembles['meta']['total_count']

    batch_predictions = world.api.list_batch_predictions()
    check_http_code(batch_predictions)
    world.init_batch_predictions_count = batch_predictions['meta']['total_count']

    clusters = world.api.list_clusters()
    check_http_code(clusters)
    world.init_clusters_count = clusters['meta']['total_count']

    centroids = world.api.list_centroids()
    check_http_code(centroids)
    world.init_centroids_count = centroids['meta']['total_count']

    batch_centroids = world.api.list_batch_centroids()
    check_http_code(batch_centroids)
    world.init_batch_centroids_count = batch_centroids['meta']['total_count']

    anomalies = world.api.list_anomalies()
    check_http_code(anomalies)
    world.init_anomalies_count = anomalies['meta']['total_count']

    anomaly_scores = world.api.list_anomaly_scores()
    check_http_code(anomaly_scores)
    world.init_anomaly_scores_count = anomaly_scores['meta']['total_count']

    batch_anomaly_scores = world.api.list_batch_anomaly_scores()
    check_http_code(batch_anomaly_scores)
    world.init_batch_anomaly_scores_count = batch_anomaly_scores['meta'][
        'total_count']


def store_final_resources():
    """Store the final existing resources grouped by resource_type

    """
    sources = world.api.list_sources()
    check_http_code(sources)
    world.final_sources_count = sources['meta']['total_count']

    datasets = world.api.list_datasets()
    check_http_code(datasets)
    world.final_datasets_count = datasets['meta']['total_count']

    models = world.api.list_models('ensemble=false')
    check_http_code(models)
    world.final_models_count = models['meta']['total_count']

    predictions = world.api.list_predictions()
    check_http_code(predictions)
    world.final_predictions_count = predictions['meta']['total_count']

    evaluations = world.api.list_evaluations()
    check_http_code(evaluations)
    world.final_evaluations_count = evaluations['meta']['total_count']

    ensembles = world.api.list_ensembles()
    check_http_code(ensembles)
    world.final_ensembles_count = ensembles['meta']['total_count']

    batch_predictions = world.api.list_batch_predictions()
    check_http_code(batch_predictions)
    world.final_batch_predictions_count = batch_predictions['meta']['total_count']

    clusters = world.api.list_clusters()
    check_http_code(clusters)
    world.final_clusters_count = clusters['meta']['total_count']

    centroids = world.api.list_centroids()
    check_http_code(centroids)
    world.final_centroids_count = centroids['meta']['total_count']

    batch_centroids = world.api.list_batch_centroids()
    check_http_code(batch_centroids)
    world.final_batch_centroids_count = batch_centroids['meta']['total_count']

    anomalies = world.api.list_anomalies()
    check_http_code(anomalies)
    world.final_anomalies_count = anomalies['meta']['total_count']

    anomaly_scores = world.api.list_anomaly_scores()
    check_http_code(anomaly_scores)
    world.final_anomaly_scores_count = anomaly_scores['meta']['total_count']

    batch_anomaly_scores = world.api.list_batch_anomaly_scores()
    check_http_code(batch_anomaly_scores)
    world.final_batch_anomaly_scores_count = batch_anomaly_scores['meta'][
        'total_count']

def check_init_equals_final():
    """Checks that the number of resources grouped by type has not changed

    """
    assert world.final_sources_count == world.init_sources_count, "init: %s, final: %s" % (world.init_sources_count, world.final_sources_count)
    assert world.final_datasets_count == world.init_datasets_count, "init: %s, final: %s" % (world.init_datasets_count, world.final_datasets_count)
    assert world.final_models_count == world.init_models_count, "init: %s, final: %s" % (world.init_models_count, world.final_models_count)
    assert world.final_predictions_count == world.init_predictions_count, "init: %s, final: %s" % (world.init_predictions_count, world.final_predictions_count)
    assert world.final_evaluations_count == world.init_evaluations_count, "init: %s, final: %s" % (world.init_evaluations_count, world.final_evaluations_count)
    assert world.final_ensembles_count == world.init_ensembles_count, "init: %s, final: %s" % (world.init_ensembles_count, world.final_ensembles_count)
    assert world.final_batch_predictions_count == world.init_batch_predictions_count, "init: %s, final: %s" % (world.init_batch_predictions_count, world.final_batch_predictions_count)
    assert world.final_clusters_count == world.init_clusters_count, "init: %s, final: %s" % (world.init_clusters_count, world.final_clusters_count)
    assert world.final_centroids_count == world.init_centroids_count, "init: %s, final: %s" % (world.init_centroids_count, world.final_centroids_count)
    assert world.final_batch_centroids_count == world.init_batch_centroids_count, "init: %s, final: %s" % (world.init_batch_centroids_count, world.final_batch_centroids_count)
    assert world.final_anomalies_count == world.init_anomalies_count, "init: %s, final: %s" % (world.init_anomalies_count, world.final_anomalies_count)
    assert world.final_anomaly_scores_count == world.init_anomaly_scores_count, "init: %s, final: %s" % (world.init_anomaly_scores_count, world.final_anomaly_scores_count)
    assert world.final_batch_anomaly_scores_count == world.init_batch_anomaly_scores_count, "init: %s, final: %s" % (world.init_batch_anomaly_scores_count, world.final_batch_anomaly_scores_count)


@step(r'I want to use api in DEV mode')
def i_want_api_dev_mode(step):
    world.api = world.api_dev_mode
    # Update counters of resources for DEV mode
    sources = world.api.list_sources()
    check_http_code(sources)
    world.init_sources_count = sources['meta']['total_count']

    datasets = world.api.list_datasets()
    check_http_code(datasets)
    world.init_datasets_count = datasets['meta']['total_count']

    models = world.api.list_models('ensemble=false')
    check_http_code(models)
    world.init_models_count = models['meta']['total_count']

    predictions = world.api.list_predictions()
    check_http_code(predictions)
    world.init_predictions_count = predictions['meta']['total_count']

    evaluations = world.api.list_evaluations()
    check_http_code(evaluations)
    world.init_evaluations_count = evaluations['meta']['total_count']

    ensembles = world.api.list_ensembles()
    check_http_code(ensembles)
    world.init_ensembles_count = ensembles['meta']['total_count']

    batch_predictions = world.api.list_batch_predictions()
    check_http_code(batch_predictions)
    world.init_batch_predictions_count = batch_predictions['meta']['total_count']

    clusters = world.api.list_clusters()
    check_http_code(clusters)
    world.init_clusters_count = clusters['meta']['total_count']

    centroids = world.api.list_centroids()
    check_http_code(centroids)
    world.init_centroids_count = centroids['meta']['total_count']

    batch_centroids = world.api.list_batch_centroids()
    check_http_code(batch_centroids)
    world.init_batch_centroids_count = batch_centroids['meta']['total_count']

    anomalies = world.api.list_anomalies()
    check_http_code(anomalies)
    world.init_anomalies_count = anomalies['meta']['total_count']

    anomaly_scores = world.api.list_anomaly_scores()
    check_http_code(anomaly_scores)
    world.init_anomaly_scores_count = anomaly_scores['meta']['total_count']

    batch_anomaly_scores = world.api.list_batch_anomaly_scores()
    check_http_code(batch_anomaly_scores)
    world.init_batch_anomaly_scores_count = batch_anomaly_scores['meta'][
        'total_count']
