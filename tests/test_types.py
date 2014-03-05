import pytest

from pypuppetdb.utils import json_to_datetime
from pypuppetdb.types import (
    Node, Fact, Resource,
    Report, Event, Catalog, Edge
    )

pytestmark = pytest.mark.unit


def test_node():
    node1 = Node('_', 'node1.puppet.board',
                 report_timestamp='2013-08-01T09:57:00.000Z',
                 catalog_timestamp='2013-08-01T09:57:00.000Z',
                 facts_timestamp='2013-08-01T09:57:00.000Z',
                 status='unreported',
                 unreported_time='0d 5h 20m',
                 )

    node2 = Node('_', 'node2.puppet.board',
                 deactivated='2013-08-01T09:57:00.000Z',
                 report_timestamp=None,
                 catalog_timestamp=None,
                 facts_timestamp=None,
                 )

    assert node1.name == 'node1.puppet.board'
    assert node1.deactivated is False
    assert node1.report_timestamp is not None
    assert node1.facts_timestamp is not None
    assert node1.catalog_timestamp is not None
    assert node1.status is 'unreported'
    assert node1.unreported_time is '0d 5h 20m'
    assert str(node1) == str('node1.puppet.board')
    assert repr(node1) == str('<Node: node1.puppet.board>')

    assert node2.name == 'node2.puppet.board'
    assert node2.deactivated is not False
    assert node2.report_timestamp is None
    assert node2.catalog_timestamp is None
    assert node2.facts_timestamp is None
    assert str(node2) == str('node2.puppet.board')
    assert repr(node2) == str('<Node: node2.puppet.board>')


def test_fact():
    fact = Fact('node1.puppet.board', 'osfamily', 'Debian')
    assert fact.node == 'node1.puppet.board'
    assert fact.name == 'osfamily'
    assert fact.value == 'Debian'
    assert str(fact) == str('osfamily/node1.puppet.board')
    assert repr(fact) == str('Fact: osfamily/node1.puppet.board')


def test_resource():
    resource = Resource('node1.puppet.board', '/etc/ssh/sshd_config', 'file',
                        ['class', 'ssh'], False, '/ssh/manifests/init.pp',
                        15, parameters={
                            'ensure': 'present',
                            'owner': 'root',
                            'group': 'root',
                            'mode': '0600',
                            })
    assert resource.node == 'node1.puppet.board'
    assert resource.name == '/etc/ssh/sshd_config'
    assert resource.type_ == 'file'
    assert resource.tags == ['class', 'ssh']
    assert resource.exported is False
    assert resource.sourcefile == '/ssh/manifests/init.pp'
    assert resource.sourceline == 15
    assert resource.parameters['ensure'] == 'present'
    assert resource.parameters['owner'] == 'root'
    assert resource.parameters['group'] == 'root'
    assert resource.parameters['mode'] == '0600'
    assert str(resource) == str('file[/etc/ssh/sshd_config]')
    assert repr(resource) == str(
        '<Resource: file[/etc/ssh/sshd_config]>')


def test_report():
    report = Report('_', 'node1.puppet.board', 'hash#',
                    '2013-08-01T09:57:00.000Z', '2013-08-01T10:57:00.000Z',
                    '2013-08-01T10:58:00.000Z', '1351535883', 3, '3.2.1',
                    'af9f16e3-75f6-4f90-acc6-f83d6524a6f3')
    assert report.node == 'node1.puppet.board'
    assert report.hash_ == 'hash#'
    assert report.start == json_to_datetime('2013-08-01T09:57:00.000Z')
    assert report.end == json_to_datetime('2013-08-01T10:57:00.000Z')
    assert report.received == json_to_datetime('2013-08-01T10:58:00.000Z')
    assert report.version == '1351535883'
    assert report.format_ == 3
    assert report.agent_version == '3.2.1'
    assert report.run_time == report.end - report.start
    assert report.transaction == 'af9f16e3-75f6-4f90-acc6-f83d6524a6f3'
    assert str(report) == str('hash#')
    assert repr(report) == str('Report: hash#')
    assert report._Report__query_scope == '["=", "report", "hash#"]'
    assert report._Report__string == 'hash#'


def test_event():
    event = Event('node1.puppet.board', 'failure', '2013-08-01T10:57:00.000Z',
                  'hash#', '/etc/ssh/sshd_config', 'ensure', 'Nothing to say',
                  'present', 'absent', 'file')

    assert event.node == 'node1.puppet.board'
    assert event.status == 'failure'
    assert event.failed is True
    assert event.timestamp == json_to_datetime('2013-08-01T10:57:00.000Z')
    assert event.hash_ == 'hash#'
    assert event.item['title'] == '/etc/ssh/sshd_config'
    assert event.item['type'] == 'file'
    assert event.item['property'] == 'ensure'
    assert event.item['message'] == 'Nothing to say'
    assert event.item['old'] == 'absent'
    assert event.item['new'] == 'present'
    assert str(event) == str('file[/etc/ssh/sshd_config]/hash#')
    assert repr(event) == str('Event: file[/etc/ssh/sshd_config]/hash#')


def test_event_failed():
    event = Event('node1.puppet.board', 'success', '2013-08-01T10:57:00.000Z',
                  'hash#', '/etc/ssh/sshd_config', 'ensure', 'Nothing to say',
                  'present', 'absent', 'file')

    assert event.status == 'success'
    assert event.failed is False


def test_catalog():
    catalog = Catalog('node1.puppet.board', [], [], 'unique', None)
    assert catalog.node == 'node1.puppet.board'
    assert catalog.version == 'unique'
    assert catalog.transaction_uuid is None
    assert catalog.resources == {}
    assert catalog.edges == []
    assert str(catalog) == str('node1.puppet.board/None')
    assert repr(catalog) == str(
        '<Catalog: node1.puppet.board/None>')


def test_edge():

    resource_a = Resource('node1.puppet.board', '/etc/ssh/sshd_config', 'file',
                          ['class', 'ssh'], False, '/ssh/manifests/init.pp',
                          15, parameters={})
    resource_b = Resource('node1.puppet.board', 'sshd', 'service',
                          ['class', 'ssh'], False, '/ssh/manifests/init.pp',
                          30, parameters={})
    edge = Edge(resource_a, resource_b, 'notify')
    assert edge.source == resource_a
    assert edge.target == resource_b
    assert edge.relationship == 'notify'
    assert str(edge) == str(
        'file[/etc/ssh/sshd_config] - notify - service[sshd]')
    assert repr(edge) == str(
        '<Edge: file[/etc/ssh/sshd_config] - notify - service[sshd]>')
