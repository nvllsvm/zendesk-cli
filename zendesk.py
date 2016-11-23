#!/usr/bin/env python3
import argparse
from configparser import ConfigParser
from getpass import getpass
from pprint import pprint
from urllib.parse import urljoin

import requests


class ZendeskAPI(object):
    def __init__(self, api_url, user, password):
        self.api_url = api_url
        self.session = requests.Session()
        self.session.auth = (user, password)

    def query(self, query):
        path = 'search.json'
        url = urljoin(self.api_url, path)
        data = {'query': query}

        next_page = True
        while next_page:
            response = self.request('GET', url, data=data)
            results = response.json()

            for ticket in results['results']:
                yield ticket

            url = results['next_page']
            if not url:
                next_page = False

    def _bulk_operation(self, method, url, tickets):
        if type(tickets) != list:
            tickets = list(tickets)

        for chunk in self._chunk_list(tickets, 100):
            ticket_batch = [str(t) for t in chunk]
            params = {'ids': ','.join(ticket_batch)}

            response = self.request(method, url, params=params)
            print(response.json()['job_status']['url'])

    def delete_spam_tickets(self, tickets):
        path = 'tickets/mark_many_as_spam.json'
        url = urljoin(self.api_url, path)
        self._bulk_operation('PUT', url, tickets)

    def delete_tickets(self, tickets):
        path = 'tickets/destroy_many.json'
        url = urljoin(self.api_url, path)
        self._bulk_operation('DELETE', url, tickets)

    def request(self, method, url, **kwargs):
        response = self.session.request(url=url, method=method, **kwargs)
        response.raise_for_status()
        return response

    def _chunk_list(self, original_list, chunk_size):
        for i in range(0, len(original_list), chunk_size):
            yield original_list[i:i+chunk_size]


def main():
    parser = argparse.ArgumentParser(description='Zendesk API CLI utility')
    parser.add_argument('query', help='API query')
    parser.add_argument('-u', '--user',
                        help='API User')
    parser.add_argument('-a', '--api-url',
                        help='API Base URL')
    parser.add_argument('-s', action='store_const',
                        const=True, dest='spam',
                        help='Delete and mark tickets as spam.')
    parser.add_argument('-d', action='store_const',
                        const=True, dest='delete',
                        help='Delete tickets.')
    parser.add_argument('-f', action='store_const',
                        const=True, dest='full_ticket',
                        help='Print full ticket data.')
    parser.add_argument('-c', '--config',
                        help='API configuration file.')
    args = parser.parse_args()

    if args.spam and args.delete:
        print('spam and delete cannot be set at the same time.')
        exit()

    if args.config:
        config = ConfigParser()
        config.read(args.config)

        user = config['zendesk-cli']['user']
        password = config['zendesk-cli']['password']
        api_url = config['zendesk-cli']['api_url']
    else:
        if args.user:
            user = args.user
            password = getpass('Password: ')
        else:
            print('Please specify the Zendesk user.')
            exit()

        if args.api_url:
            api_url = args.api_url
        else:
            print('Please specify the API URL.')
            exit()

    zd = ZendeskAPI(api_url, user, password)

    tickets = []
    for ticket in zd.query(args.query):
        if args.full_ticket:
            pprint(ticket)
        else:
            try:
                print('{}  {}'.format(ticket['id'],
                                      ticket['subject']))
            except KeyError:
                print(ticket['id'])
        tickets.append(ticket['id'])
        if len(tickets) >= 100:
            if args.spam:
                zd.delete_spam_tickets(tickets)
            elif args.delete:
                zd.delete_tickets(tickets)
            tickets = []

    if tickets:
        if args.spam:
            zd.delete_spam_tickets(tickets)
        elif args.delete:
            zd.delete_tickets(tickets)


if __name__ == '__main__':
    main()
