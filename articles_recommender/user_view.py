from datetime import datetime

from constants import BASE_TOPIC_PIORITT, BASE_TOPIC_WEIGHT, PREFERENCE_TOPIC_PIORITT, MAX_ARTICLE_COUNT, PIORITY_STEP


class UserView:
    def __init__(self, user_id, last_visited, preferences, topic_piorities, previous_viewed_articles):
        self.user_id = user_id
        self.last_visited = last_visited
        self.preferences = preferences
        self.topic_piorities = topic_piorities
        self.previous_viewed_articles = previous_viewed_articles

    def check_first_time_visit_today(self, topics):
        first_time = self.last_visited.date() != datetime.now().date()
        if first_time or self.topic_piorities is None or self.previous_viewed_articles is None:
            self.last_visited = datetime.now()
            print("First time visit today")
            self._reset_view(topics)

        return first_time

    def _reset_view(self, topics):
        self.previous_viewed_articles = {topic: "" for topic in topics}
        self.topic_pointers = {topic: "" for topic in topics}
        self.topic_piorities = {topic: BASE_TOPIC_PIORITT for topic in topics}
        for topic in topics:
            if topic in self.preferences:
                self.topic_piorities[topic] = PREFERENCE_TOPIC_PIORITT

    def get_articles_count_for_topics(self, topics):
        topic_weights = self._calculate_topic_weight_percents(topics)
        articles_count = {}
        for topic in topics:
            articles_count[topic] = int(topic_weights[topic] * MAX_ARTICLE_COUNT)
        print(f"- Articles count matrix: {articles_count}")
        return articles_count

    def _calculate_topic_weight_percents(self, topics):
        topic_weights = {}
        total_weight = 0
        for topic in topics:
            bonus_weight = topics[topic]["bonus_weight"] if "bonus_weight" in topics[topic] else 0
            weight = BASE_TOPIC_WEIGHT * self.topic_piorities[topic] + bonus_weight
            total_weight += weight
            topic_weights[topic] = weight
        for topic in topics:
            topic_weights[topic] = round((topic_weights[topic] / total_weight), 2)
        print(f"- Weight matrix: {topic_weights}")
        return topic_weights

    def adjust_topic_piorities(self):
        max_piority_topic = max(self.topic_piorities, key=self.topic_piorities.get)
        min_piority_topic = min(self.topic_piorities, key=self.topic_piorities.get)
        self.topic_piorities[max_piority_topic] = round(self.topic_piorities[max_piority_topic] - PIORITY_STEP, 1)
        if (min_piority_topic != max_piority_topic):
            self.topic_piorities[min_piority_topic] = round(self.topic_piorities[min_piority_topic] + PIORITY_STEP, 1)
        print(f"- Piority matrix: {self.topic_piorities}")
